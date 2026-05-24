import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class Logger:
    def __init__(self, name: str, log_dir: Optional[str] = None):
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else None
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def LogInfo(self, message: str) -> None:
        print(f"[{self.name}] {message}")
    
    def LogDebug(self, message: str) -> None:
        print(f"[{self.name}:DEBUG] {message}")
    
    def LogWarning(self, message: str) -> None:
        print(f"[{self.name}:WARNING] {message}")
    
    def LogError(self, message: str) -> None:
        print(f"[{self.name}:ERROR] {message}")
    
    def LogMetric(self, metric_name: str, value: Any) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
        }
        print(f"[{self.name}:METRIC] {json.dumps(entry)}")
