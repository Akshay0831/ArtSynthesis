from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


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
    stage_1_time_sec: float = 0.0
    stage_2_time_sec: float = 0.0
    stage_3_time_sec: float = 0.0
    peak_vram_gb: float = 0.0
    peak_ram_gb: float = 0.0
    total_parts_extracted: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def total_time_sec(self) -> float:
        return self.stage_1_time_sec + self.stage_2_time_sec + self.stage_3_time_sec
    
    def to_dict(self) -> dict:
        return {
            "stream_id": self.stream_id,
            "seed": self.seed,
            "stage_1_time_sec": self.stage_1_time_sec,
            "stage_2_time_sec": self.stage_2_time_sec,
            "stage_3_time_sec": self.stage_3_time_sec,
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
    current_stage: int = 0
    completed_regions: list[str] = field(default_factory=list)
    hero_generated: bool = False
    sheet_complete: bool = False
    rig_complete: bool = False
    metrics: Optional[PerformanceMetrics] = None
    error_message: Optional[str] = None
