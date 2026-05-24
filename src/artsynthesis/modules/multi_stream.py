from typing import List, Optional
from dataclasses import dataclass


@dataclass
class MultiStreamConfig:
    num_streams: int = 4
    enable_parallel_processing: bool = True
    max_concurrent_streams: int = None


class MultiStream:
    def __init__(self, config: MultiStreamConfig = None):
        self.config = config or MultiStreamConfig()
    
    def GetStreamCount(self) -> int:
        return self.config.num_streams
    
    def IsEnabled(self) -> bool:
        return self.config.enable_parallel_processing and self.config.num_streams > 1
