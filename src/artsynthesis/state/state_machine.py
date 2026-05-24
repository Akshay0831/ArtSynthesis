from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict


class GenerationState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PerformanceMetrics:
    stream_id: int
    seed: int
    stage_times: Dict[str, float] = field(default_factory=dict)
    peak_vram_gb: float = 0.0
    peak_ram_gb: float = 0.0
    total_parts_extracted: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def total_time_sec(self) -> float:
        return sum(self.stage_times.values())
    
    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "seed": self.seed,
            "stage_times": self.stage_times,
            "total_time_sec": self.total_time_sec,
            "peak_vram_gb": self.peak_vram_gb,
            "peak_ram_gb": self.peak_ram_gb,
            "total_parts_extracted": self.total_parts_extracted,
            "timestamp": self.timestamp,
        }


@dataclass
class StreamState:
    stream_id: int
    seed: int
    state: GenerationState = GenerationState.IDLE
    current_stage_index: int = 0
    completed_stages: list[str] = field(default_factory=list)
    metrics: Optional[PerformanceMetrics] = None
    error_message: Optional[str] = None
