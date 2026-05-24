import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any


class Logger:
    def __init__(self, name: str, log_dir: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Avoid duplicate handlers if the logger is re-initialized
        if not self.logger.handlers:
            self.logger.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                fmt="[%(asctime)s] [%(name)s:%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            
            # Console Handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            
            # File Handler
            if log_dir:
                log_path = Path(log_dir)
                log_path.mkdir(parents=True, exist_ok=True)
                fh = logging.FileHandler(log_path / f"{name}.log")
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)

    def LogInfo(self, message: str) -> None:
        self.logger.info(message)
    
    def LogDebug(self, message: str) -> None:
        self.logger.debug(message)
    
    def LogWarning(self, message: str) -> None:
        self.logger.warning(message)
    
    def LogError(self, message: str) -> None:
        self.logger.error(message, exc_info=True if self.logger.isEnabledFor(logging.DEBUG) else False)
    
    def LogMetric(self, metric_name: str, value: Any) -> None:
        """Logs a metric in JSON format for automated parsing."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "metric": metric_name,
            "value": value,
        }
        self.logger.info(f"METRIC: {json.dumps(entry)}")
