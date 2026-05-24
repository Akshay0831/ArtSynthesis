from typing import List, Tuple
from artsynthesis.config.schema import ArtGenerationConfig, PartDefinition


class ValidationError(Exception):
    pass


class ConfigValidator:
    @staticmethod
    def Validate(config: ArtGenerationConfig) -> tuple[bool, list[str]]:
        errors = []
        
        errors.extend(ConfigValidator._ValidateGeneration(config))
        errors.extend(ConfigValidator._ValidateLayout(config))
        errors.extend(ConfigValidator._ValidatePrompts(config))
        errors.extend(ConfigValidator._ValidateExport(config))
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _ValidateGeneration(config: ArtGenerationConfig) -> list[str]:
        errors = []
        gen = config.generation
        
        if gen.num_streams < 1:
            errors.append("num_streams must be >= 1")
        
        if gen.num_streams > 16:
            errors.append("num_streams should not exceed 16 for safety")
        
        if gen.ip_adapter_mode not in ["single", "dual"]:
            errors.append(f"ip_adapter_mode must be 'single' or 'dual', got '{gen.ip_adapter_mode}'")
        
        return errors
    
    @staticmethod
    def _ValidateLayout(config: ArtGenerationConfig) -> list[str]:
        errors = []
        layout = config.layout
        
        if layout.canvas_width < 256:
            errors.append("canvas_width must be >= 256")
        
        if layout.canvas_height < 256:
            errors.append("canvas_height must be >= 256")
        
        if not layout.parts:
            errors.append("At least one part must be defined")
        
        for part in layout.parts:
            part_errors = ConfigValidator._ValidatePart(part, layout)
            errors.extend(part_errors)
        
        return errors
    
    @staticmethod
    def _ValidatePart(part: PartDefinition, layout) -> list[str]:
        errors = []
        
        if not part.name:
            errors.append("Part name cannot be empty")
        
        if part.width < 1 or part.height < 1:
            errors.append(f"Part '{part.name}' has invalid dimensions")
        
        if part.x + part.width > layout.canvas_width:
            errors.append(f"Part '{part.name}' exceeds canvas width")
        
        if part.y + part.height > layout.canvas_height:
            errors.append(f"Part '{part.name}' exceeds canvas height")
        
        return errors
    
    @staticmethod
    def _ValidatePrompts(config: ArtGenerationConfig) -> list[str]:
        errors = []
        
        if not config.prompts.hero:
            errors.append("Hero prompt cannot be empty")
        
        return errors
    
    @staticmethod
    def _ValidateExport(config: ArtGenerationConfig) -> list[str]:
        errors = []
        
        if not config.export.formats:
            errors.append("At least one export format must be specified")
        
        valid_formats = ["png", "depth", "metadata", "normals", "ao"]
        for fmt in config.export.formats:
            if fmt not in valid_formats:
                errors.append(f"Unknown export format: {fmt}")
        
        return errors
