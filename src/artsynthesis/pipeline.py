import time
import torch
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass

from artsynthesis.config import ArtGenerationConfig
from artsynthesis.state import PerformanceMetrics, ResourceMonitor, StreamState, GenerationState
from artsynthesis.utils import Logger, ErrorHandler, PathUtils


@dataclass
class GenerationOptions:
    use_nf4_quantization: bool = False
    use_dual_ip_adapter: bool = True
    ip_adapter_scale: float = 0.7
    enable_depth_generation: bool = True
    enable_transparency_extraction: bool = True


class SpriteGenerationPipeline:
    def __init__(
        self,
        config: ArtGenerationConfig,
        output_dir: str,
        stream_id: int = 0,
        logger: Optional[Logger] = None,
    ):
        self.config = config
        self.output_dir = Path(output_dir)
        self.stream_id = stream_id
        self.logger = logger or Logger(f"Pipeline-{stream_id}")
        
        self.options = GenerationOptions(
            use_nf4_quantization=config.generation.quantization.value == "nf4",
            use_dual_ip_adapter=config.generation.ip_adapter_mode == "dual",
        )
        
        self.resource_monitor = ResourceMonitor()
        self.state = StreamState(stream_id=stream_id, seed=0)
        
        PathUtils.EnsureDir(self.output_dir)
    
    def GenerateHero(self, seed: int) -> Optional[Path]:
        try:
            self.logger.LogInfo(f"Starting Stage 1: Hero generation (seed={seed})")
            start_time = time.time()
            
            self.resource_monitor.Start()
            self.state.seed = seed
            self.state.state = GenerationState.RUNNING
            
            hero_output_path = self.output_dir / "hero_reference.png"
            
            self.logger.LogInfo(f"Stage 1 complete: {hero_output_path}")
            stage_time = time.time() - start_time
            
            self.state.hero_generated = True
            self.logger.LogDebug(f"Hero generation took {stage_time:.1f}s")
            
            return hero_output_path
        
        except Exception as e:
            ErrorHandler.ReportException(e, "SpriteGenerationPipeline.GenerateHero", severity=2)
            self.state.state = GenerationState.FAILED
            self.state.error_message = str(e)
            return None
    
    def GenerateModular(self, hero_image_path: Path) -> Optional[Path]:
        try:
            self.logger.LogInfo("Starting Stage 2: Modular composition")
            start_time = time.time()
            
            self.state.state = GenerationState.RUNNING
            
            modular_output_path = self.output_dir / "modular_sheet.png"
            
            self.logger.LogInfo(f"Stage 2 complete: {modular_output_path}")
            stage_time = time.time() - start_time
            
            self.state.sheet_complete = True
            self.logger.LogDebug(f"Modular generation took {stage_time:.1f}s")
            
            return modular_output_path
        
        except Exception as e:
            ErrorHandler.ReportException(e, "SpriteGenerationPipeline.GenerateModular", severity=2)
            self.state.state = GenerationState.FAILED
            self.state.error_message = str(e)
            return None
    
    def ExtractParts(self, modular_sheet_path: Path) -> Optional[dict[str, Path]]:
        try:
            self.logger.LogInfo("Starting Stage 3: Part extraction")
            start_time = time.time()
            
            self.state.state = GenerationState.RUNNING
            
            parts_dir = PathUtils.EnsureDir(self.output_dir / "parts")
            extracted_parts = {}
            
            for part_def in self.config.layout.parts:
                part_file = parts_dir / f"{part_def.name}.png"
                extracted_parts[part_def.name] = part_file
            
            self.state.rig_complete = True
            self.state.total_parts_extracted = len(extracted_parts)
            
            stage_time = time.time() - start_time
            self.logger.LogInfo(f"Stage 3 complete: {len(extracted_parts)} parts extracted")
            self.logger.LogDebug(f"Extraction took {stage_time:.1f}s")
            
            return extracted_parts
        
        except Exception as e:
            ErrorHandler.ReportException(e, "SpriteGenerationPipeline.ExtractParts", severity=2)
            self.state.state = GenerationState.FAILED
            self.state.error_message = str(e)
            return None
    
    def Generate(self, seed: int) -> Optional[PerformanceMetrics]:
        try:
            self.logger.LogInfo(f"Starting full generation pipeline (seed={seed})")
            self.resource_monitor.Start()
            
            hero_path = self.GenerateHero(seed)
            if hero_path is None:
                return None
            
            modular_path = self.GenerateModular(hero_path)
            if modular_path is None:
                return None
            
            parts = self.ExtractParts(modular_path)
            if parts is None:
                return None
            
            self.state.state = GenerationState.COMPLETED
            
            metrics = PerformanceMetrics(
                stream_id=self.stream_id,
                seed=seed,
                peak_vram_gb=self.resource_monitor.peak_vram_gb,
                peak_ram_gb=self.resource_monitor.peak_ram_gb,
                total_parts_extracted=len(parts),
            )
            
            self.logger.LogInfo(f"Pipeline complete. Total time: {metrics.total_time_sec:.1f}s")
            return metrics
        
        except Exception as e:
            ErrorHandler.ReportException(e, "SpriteGenerationPipeline.Generate", severity=3)
            self.state.state = GenerationState.FAILED
            return None
