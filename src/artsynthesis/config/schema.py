from typing import Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class ModelType(Enum):
    SDXL = "sdxl"
    FLUX = "flux"


class QuantizationType(Enum):
    NF4 = "nf4"
    FP8 = "fp8"
    NONE = "none"


class StageType(Enum):
    TEXT_TO_IMAGE = "text_to_image"
    IMAGE_TO_IMAGE = "image_to_image"
    INPAINTING = "inpainting"
    SEGMENTATION = "segmentation"
    DEPTH_EXTRACTION = "depth_extraction"
    BACKGROUND_REMOVAL = "background_removal"
    UPSCALE = "upscale"


@dataclass
class StageConfig:
    name: str
    type: StageType
    prompt: str = ""
    negative_prompt: str = ""
    input_source: Optional[str] = None  # Name of a previous stage
    params: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: dict) -> "StageConfig":
        return StageConfig(
            name=data.get("name", "unnamed_stage"),
            type=StageType(data.get("type", "text_to_image")),
            prompt=data.get("prompt", ""),
            negative_prompt=data.get("negative_prompt", ""),
            input_source=data.get("input_source"),
            params=data.get("params", {}),
        )


@dataclass
class PartDefinition:
    name: str
    x: int
    y: int
    width: int
    height: int
    parent: Optional[str] = None


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
class ExportConfig:
    formats: list[str] = field(default_factory=lambda: ["png"])
    output_dir: str = "./output"
    save_intermediate: bool = True
    
    @staticmethod
    def from_dict(data: dict) -> "ExportConfig":
        return ExportConfig(
            formats=data.get("formats", ["png"]),
            output_dir=data.get("output_dir", "./output"),
            save_intermediate=data.get("save_intermediate", True),
        )


class SeedStrategy(Enum):
    FIXED = "fixed"
    RANDOM = "random"
    DESIGN_VARIATION = "design_variation"


@dataclass
class PromptConfig:
    positive: str = ""
    negative: str = ""


@dataclass
class ReferenceConfig:
    enable_search: bool = True
    index_path: str = "./references"


@dataclass
class GlobalConfig:
    model: ModelType = ModelType.SDXL
    quantization: QuantizationType = QuantizationType.NONE
    device: str = "auto"
    enable_multi_stream: bool = True
    num_streams: int = 1
    enable_pause_resume: bool = True
    model_paths: dict[str, str] = field(default_factory=dict)
    
    @staticmethod
    def from_dict(data: dict) -> "GlobalConfig":
        return GlobalConfig(
            model=ModelType(data.get("model", "sdxl")),
            quantization=QuantizationType(data.get("quantization", "none")),
            device=data.get("device", "auto"),
            enable_multi_stream=data.get("enable_multi_stream", True),
            num_streams=data.get("num_streams", 1),
            enable_pause_resume=data.get("enable_pause_resume", True),
            model_paths=data.get("model_paths", {}),
        )


@dataclass
class ArtGenerationConfig:
    globals: GlobalConfig = field(default_factory=GlobalConfig)
    pipeline: list[StageConfig] = field(default_factory=list)
    layout: Optional[LayoutConfig] = None
    export: ExportConfig = field(default_factory=ExportConfig)
    
    @staticmethod
    def from_dict(data: dict) -> "ArtGenerationConfig":
        return ArtGenerationConfig(
            globals=GlobalConfig.from_dict(data.get("globals", {})),
            pipeline=[StageConfig.from_dict(s) for s in data.get("pipeline", [])],
            layout=LayoutConfig.from_dict(data.get("layout", {})) if "layout" in data else None,
            export=ExportConfig.from_dict(data.get("export", {})),
        )
