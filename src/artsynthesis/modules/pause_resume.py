from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class PauseResumeConfig:
    enable_checkpointing: bool = True
    checkpoint_interval_sec: float = 300.0
    checkpoint_dir: str = "./checkpoints"


class PauseResume:
    def __init__(self, config: PauseResumeConfig = None):
        self.config = config or PauseResumeConfig()
        self.checkpoint_dir = Path(self.config.checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def IsEnabled(self) -> bool:
        return self.config.enable_checkpointing
    
    def GetCheckpointDir(self) -> Path:
        return self.checkpoint_dir
