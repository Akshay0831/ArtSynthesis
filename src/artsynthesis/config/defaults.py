from artsynthesis.config.schema import (
    ArtGenerationConfig,
    GenerationConfig,
    LayoutConfig,
    PromptConfig,
    ExportConfig,
    ReferenceConfig,
    PartDefinition,
    ModelType,
    SeedStrategy,
)


def GetDefaultConfig() -> ArtGenerationConfig:
    return ArtGenerationConfig(
        generation=GenerationConfig(
            model=ModelType.SDXL,
            num_streams=1,
            seed_strategy=SeedStrategy.DESIGN_VARIATION,
            enable_pause_resume=True,
            enable_feedback=True,
            enable_reference_search=True,
            enable_rl_training=False,
            ip_adapter_mode="dual",
        ),
        layout=LayoutConfig(
            canvas_width=1024,
            canvas_height=1024,
            parts=[
                PartDefinition(name="head", x=0, y=0, width=256, height=256),
                PartDefinition(name="torso", x=256, y=0, width=256, height=256),
                PartDefinition(name="upper_arm_l", x=512, y=0, width=128, height=256),
                PartDefinition(name="upper_arm_r", x=640, y=0, width=128, height=256),
                PartDefinition(name="lower_arm_l", x=768, y=0, width=128, height=256),
                PartDefinition(name="lower_arm_r", x=896, y=0, width=128, height=256),
                PartDefinition(name="upper_leg_l", x=0, y=256, width=128, height=256),
                PartDefinition(name="upper_leg_r", x=128, y=256, width=128, height=256),
                PartDefinition(name="lower_leg_l", x=256, y=256, width=128, height=256),
                PartDefinition(name="lower_leg_r", x=384, y=256, width=128, height=256),
                PartDefinition(name="weapon", x=512, y=256, width=256, height=256),
            ],
        ),
        prompts=PromptConfig(
            hero="Professional character illustration",
            negative="blurry, low quality, distorted",
            regional_overrides={},
        ),
        export=ExportConfig(
            formats=["png", "depth", "metadata"],
            output_dir="./output",
        ),
        references=ReferenceConfig(
            enable_search=True,
            index_path="./references",
        ),
    )
