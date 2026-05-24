import threading
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

from artsynthesis.config import ArtGenerationConfig, ConfigLoader, ConfigValidator
from artsynthesis.pipeline import SpriteGenerationPipeline
from artsynthesis.state import PerformanceMetrics, StreamState, GenerationState, CheckpointManager
from artsynthesis.utils import Logger, PathUtils, ErrorHandler


@dataclass
class GenerationFeedback:
    stream_id: int
    feedback_type: str
    score: int
    comment: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class GenerationOrchestrator:
    def __init__(
        self,
        config: ArtGenerationConfig,
        output_dir: str = "./output",
        num_streams: int = 1,
    ):
        self.config = config
        self.output_dir = Path(output_dir)
        self.num_streams = num_streams
        
        self.logger = Logger("GenerationOrchestrator")
        PathUtils.EnsureDir(self.output_dir)
        
        self.streams: dict[int, SpriteGenerationPipeline] = {}
        self.stream_states: dict[int, StreamState] = {}
        self.stream_pause_events: dict[int, threading.Event] = {}
        
        self.metrics: list[PerformanceMetrics] = []
        self.feedback: list[GenerationFeedback] = []
        
        self.checkpoint_manager = CheckpointManager(str(self.output_dir / "checkpoints"))
    
    def ValidateConfig(self) -> tuple[bool, list[str]]:
        is_valid, errors = ConfigValidator.Validate(self.config)
        
        if is_valid:
            self.logger.LogInfo("Configuration validated successfully")
        else:
            self.logger.LogError(f"Configuration validation failed: {errors}")
        
        return is_valid, errors
    
    def GenerateBatch(self, seeds: list[int]) -> list[PerformanceMetrics]:
        is_valid, errors = self.ValidateConfig()
        if not is_valid:
            raise ValueError(f"Invalid configuration: {errors}")
        
        if not self.config.generation.enable_multi_stream and len(seeds) > 1:
            raise ValueError("Multi-stream disabled in config, provide single seed")
        
        self.logger.LogInfo(f"Starting batch generation: {len(seeds)} seeds, {self.num_streams} streams")
        
        self.metrics = []
        
        for stream_id, seed in enumerate(seeds):
            if stream_id >= self.num_streams:
                break
            
            stream_dir = PathUtils.EnsureDir(self.output_dir / f"stream_{stream_id:02d}_seed_{seed:06d}")
            
            pipeline = SpriteGenerationPipeline(
                config=self.config,
                output_dir=str(stream_dir),
                stream_id=stream_id,
                logger=Logger(f"Stream-{stream_id}"),
            )
            
            self.streams[stream_id] = pipeline
            
            self.stream_pause_events[stream_id] = threading.Event()
            self.stream_pause_events[stream_id].set()
            
            try:
                metrics = pipeline.Generate(seed)
                if metrics:
                    self.metrics.append(metrics)
                    self.checkpoint_manager.SaveCheckpoint(pipeline.state)
            except Exception as e:
                ErrorHandler.ReportException(e, f"Stream-{stream_id}", severity=2)
        
        self.logger.LogInfo(f"Batch generation complete: {len(self.metrics)} successful")
        return self.metrics
    
    def PauseStream(self, stream_id: int) -> None:
        if stream_id not in self.stream_pause_events:
            self.logger.LogWarning(f"Stream {stream_id} not found")
            return
        
        self.stream_pause_events[stream_id].clear()
        self.logger.LogInfo(f"Stream {stream_id} paused")
    
    def ResumeStream(self, stream_id: int) -> None:
        if stream_id not in self.stream_pause_events:
            self.logger.LogWarning(f"Stream {stream_id} not found")
            return
        
        self.stream_pause_events[stream_id].set()
        self.logger.LogInfo(f"Stream {stream_id} resumed")
    
    def PauseAll(self) -> None:
        for stream_id in self.stream_pause_events:
            self.stream_pause_events[stream_id].clear()
        self.logger.LogInfo("All streams paused")
    
    def ResumeAll(self) -> None:
        for stream_id in self.stream_pause_events:
            self.stream_pause_events[stream_id].set()
        self.logger.LogInfo("All streams resumed")
    
    def SubmitFeedback(self, stream_id: int, feedback_type: str, score: int, comment: str = "") -> None:
        if not (1 <= score <= 10):
            raise ValueError(f"Score must be between 1 and 10, got {score}")
        
        feedback = GenerationFeedback(
            stream_id=stream_id,
            feedback_type=feedback_type,
            score=score,
            comment=comment,
        )
        
        self.feedback.append(feedback)
        self.logger.LogInfo(f"Feedback recorded: Stream {stream_id}, {feedback_type}={score}")
    
    def GetStreamStatus(self, stream_id: int) -> Optional[dict]:
        if stream_id not in self.streams:
            return None
        
        pipeline = self.streams[stream_id]
        
        return {
            "stream_id": stream_id,
            "seed": pipeline.state.seed,
            "state": pipeline.state.state.value,
            "stage": pipeline.state.current_stage,
            "hero_generated": pipeline.state.hero_generated,
            "sheet_complete": pipeline.state.sheet_complete,
            "rig_complete": pipeline.state.rig_complete,
        }
    
    def Finalize(self) -> None:
        self.logger.LogInfo("Finalizing generation")
        
        metrics_file = self.output_dir / "metrics.json"
        feedback_file = self.output_dir / "feedback.json"
        
        import json
        
        with open(metrics_file, "w") as f:
            json.dump([m.to_dict() for m in self.metrics], f, indent=2)
        
        with open(feedback_file, "w") as f:
            feedback_data = [
                {
                    "stream_id": f.stream_id,
                    "type": f.feedback_type,
                    "score": f.score,
                    "comment": f.comment,
                    "timestamp": f.timestamp,
                }
                for f in self.feedback
            ]
            json.dump(feedback_data, f, indent=2)
        
        self.logger.LogInfo(f"Finalization complete. Metrics saved to {metrics_file}")
