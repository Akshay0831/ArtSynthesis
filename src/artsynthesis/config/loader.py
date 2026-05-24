import json
import yaml
from pathlib import Path
from typing import Optional
from artsynthesis.config.schema import ArtGenerationConfig
from artsynthesis.config.defaults import GetDefaultConfig


class ConfigError(Exception):
    pass


class ConfigLoader:
    @staticmethod
    def Load(config_path: str) -> ArtGenerationConfig:
        path = Path(config_path)
        
        if not path.exists():
            raise ConfigError(f"Config file not found: {config_path}")
        
        try:
            if path.suffix.lower() in [".json"]:
                with open(path, "r") as f:
                    data = json.load(f)
            elif path.suffix.lower() in [".yaml", ".yml"]:
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
            else:
                raise ConfigError(f"Unsupported config format: {path.suffix}")
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config: {e}") from e
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config: {e}") from e
        
        try:
            config = ArtGenerationConfig.from_dict(data)
            return config
        except (KeyError, ValueError, TypeError) as e:
            raise ConfigError(f"Invalid config structure: {e}") from e
    
    @staticmethod
    def LoadWithDefaults(config_path: Optional[str] = None) -> ArtGenerationConfig:
        if config_path is None:
            return GetDefaultConfig()
        
        return ConfigLoader.Load(config_path)
