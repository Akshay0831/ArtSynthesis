from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ModelType(Enum):
    SDXL = "sdxl"
    FLUX = "flux"


class QuantizationType(Enum):
    NF4 = "nf4"
    FP8 = "fp8"
    NONE = "none"


class SeedStrategy(Enum):
    DESIGN_VARIATION = "design_variation"
    RANDOM = "random"


@dataclass
class PartDefinition:
    name: str
    x: int
    y: int
    width: int
    height: int


@dataclass
class GenerationConfig:
    model: ModelType = ModelType.SDXL
    enable_multi_stream: bool = True
    num_streams: int = 1
    seed_strategy: SeedStrategy = SeedStrategy.DESIGN_VARIATION
    enable_pause_resume: bool = True
    enable_feedback: bool = True
    enable_reference_search: bool = True
    enable_rl_training: bool = False
    ip_adapter_mode: str = "dual"
    quantization: QuantizationType = QuantizationType.NONE
    
    @staticmethod
    def from_dict(data: dict) -> "GenerationConfig":
        return GenerationConfig(
            model=ModelType(data.get("model", "sdxl")),
            enable_multi_stream=data.get("enable_multi_stream", True),
            num_streams=data.get("num_streams", 1),
            seed_strategy=SeedStrategy(data.get("seed_strategy", "design_variation")),
            enable_pause_resume=data.get("enable_pause_resume", True),
            enable_feedback=data.get("enable_feedback", True),
            enable_reference_search=data.get("enable_reference_search", True),
            enable_rl_training=data.get("enable_rl_training", False),
            ip_adapter_mode=data.get("ip_adapter_mode", "dual"),
            quantization=QuantizationType(data.get("quantization", "none")),
        )


@dataclass
class LayoutConfig:
    canvas_width: int = 1024
    canvas_height: int = 1024
    parts: list[PartDefinition] = field(default_factory=list)
    
    @staticmethod
    def from_dict(data: dict) -> "LayoutConfig":
        parts = [
            PartDefinition(**part) for part in data.get("parts", [])
        ]
        return LayoutConfig(
            canvas_width=data.get("canvas_width", 1024),
            canvas_height=data.get("canvas_height", 1024),
            parts=parts,
        )


@dataclass
class PromptConfig:
    hero: str = ""
    negative: str = ""
    regional_overrides: dict[str, str] = field(default_factory=dict)
    
    @staticmethod
    def from_dict(data: dict) -> "PromptConfig":
        return PromptConfig(
            hero=data.get("hero", ""),
            negative=data.get("negative", ""),
            regional_overrides=data.get("regional_overrides", {}),
        )


@dataclass
class ExportConfig:
    formats: list[str] = field(default_factory=lambda: ["png"])
    output_dir: str = "./output"
    
    @staticmethod
    def from_dict(data: dict) -> "ExportConfig":
        return ExportConfig(
            formats=data.get("formats", ["png"]),
            output_dir=data.get("output_dir", "./output"),
        )


@dataclass
class ReferenceConfig:
    enable_search: bool = True
    index_path: str = "./references"
    
    @staticmethod
    def from_dict(data: dict) -> "ReferenceConfig":
        return ReferenceConfig(
            enable_search=data.get("enable_search", True),
            index_path=data.get("index_path", "./references"),
        )


@dataclass
class ArtGenerationConfig:
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    prompts: PromptConfig = field(default_factory=PromptConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    references: ReferenceConfig = field(default_factory=ReferenceConfig)
    
    @staticmethod
    def from_dict(data: dict) -> "ArtGenerationConfig":
        return ArtGenerationConfig(
            generation=GenerationConfig.from_dict(data.get("generation", {})),
            layout=LayoutConfig.from_dict(data.get("layout", {})),
            prompts=PromptConfig.from_dict(data.get("prompts", {})),
            export=ExportConfig.from_dict(data.get("export", {})),
            references=ReferenceConfig.from_dict(data.get("references", {})),
        )
