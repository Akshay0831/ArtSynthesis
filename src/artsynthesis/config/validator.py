from artsynthesis.config.schema import ArtGenerationConfig


class ValidationError(Exception):
    pass


class ConfigValidator:
    @staticmethod
    def Validate(config: ArtGenerationConfig) -> tuple[bool, list[str]]:
        errors = []
        
        # 1. Validate Globals
        if config.globals.num_streams < 1:
            errors.append("globals.num_streams must be at least 1")
            
        # 2. Validate Pipeline
        if not config.pipeline:
            errors.append("pipeline must contain at least one stage")
            
        stage_names = set()
        for i, stage in enumerate(config.pipeline):
            # Unique names
            if not stage.name or stage.name == "unnamed_stage":
                errors.append(f"Stage at index {i} must have a unique name")
            elif stage.name in stage_names:
                errors.append(f"Duplicate stage name: '{stage.name}'")
            stage_names.add(stage.name)
            
            # Input source resolution
            if stage.input_source:
                if stage.input_source not in stage_names:
                    errors.append(f"Stage '{stage.name}' references non-existent input_source: '{stage.input_source}'")
                elif stage.input_source == stage.name:
                    errors.append(f"Stage '{stage.name}' cannot use itself as input_source")
        
        # 3. Validate Layout (Optional)
        if config.layout:
            if config.layout.canvas_width <= 0 or config.layout.canvas_height <= 0:
                errors.append("layout dimensions must be positive")
                
            part_names = set()
            for part in config.layout.parts:
                if not part.name:
                    errors.append("All layout parts must have a name")
                elif part.name in part_names:
                    errors.append(f"Duplicate layout part name: '{part.name}'")
                part_names.add(part.name)
                
                # Bounds check
                if part.x < 0 or part.y < 0:
                    errors.append(f"Part '{part.name}' coordinates cannot be negative")
                if part.x + part.width > config.layout.canvas_width:
                    errors.append(f"Part '{part.name}' exceeds canvas width")
                if part.y + part.height > config.layout.canvas_height:
                    errors.append(f"Part '{part.name}' exceeds canvas height")
        
        return len(errors) == 0, errors
