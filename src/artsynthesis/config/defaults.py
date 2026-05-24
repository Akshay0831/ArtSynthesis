from artsynthesis.config.schema import (
    ArtGenerationConfig,
    GlobalConfig,
    StageConfig,
    StageType,
    ExportConfig,
    ModelType,
    QuantizationType,
)


def GetDefaultConfig() -> ArtGenerationConfig:
    """Returns a generic default configuration for text-to-image generation."""
    return ArtGenerationConfig(
        globals=GlobalConfig(
            model=ModelType.SDXL,
            quantization=QuantizationType.NONE,
            num_streams=1,
            enable_multi_stream=True,
        ),
        pipeline=[
            StageConfig(
                name="base_generation",
                type=StageType.TEXT_TO_IMAGE,
                prompt="A beautiful landscape, digital art",
                negative_prompt="blurry, low quality",
                params={"width": 1024, "height": 1024, "steps": 30}
            )
        ],
        export=ExportConfig(
            formats=["png"],
            output_dir="./output",
            save_intermediate=True
        )
    )
