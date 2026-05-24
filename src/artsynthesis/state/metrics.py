import psutil
import torch
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ResourceSnapshot:
    vram_gb: float = 0.0
    ram_gb: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ResourceMonitor:
    def __init__(self):
        self.peak_vram_gb = 0.0
        self.peak_ram_gb = 0.0
        self.start_time: Optional[float] = None
    
    def Start(self) -> None:
        import time
        self.start_time = time.time()
        torch.cuda.reset_peak_memory_stats()
        self.peak_vram_gb = 0.0
        self.peak_ram_gb = 0.0
    
    def Update(self) -> ResourceSnapshot:
        vram_gb = 0.0
        if torch.cuda.is_available():
            vram_gb = torch.cuda.memory_allocated() / (1024 ** 3)
            self.peak_vram_gb = max(self.peak_vram_gb, vram_gb)
        
        ram_gb = psutil.Process().memory_info().rss / (1024 ** 3)
        self.peak_ram_gb = max(self.peak_ram_gb, ram_gb)
        
        return ResourceSnapshot(vram_gb=vram_gb, ram_gb=ram_gb)
    
    @property
    def elapsed_sec(self) -> float:
        if self.start_time is None:
            return 0.0
        import time
        return time.time() - self.start_time
