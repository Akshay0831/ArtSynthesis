import time
import torch
import rembg
from pathlib import Path
from typing import Optional, Any, Dict, List
from PIL import Image

from artsynthesis.config import ArtGenerationConfig, StageConfig, StageType
from artsynthesis.state import PerformanceMetrics, ResourceMonitor, StreamState, GenerationState
from artsynthesis.utils import Logger, ErrorHandler, PathUtils, DeviceUtils
from artsynthesis.modules import ModelManager


class SpriteGenerationPipeline:
    def __init__(
        self,
        config: ArtGenerationConfig,
        output_dir: str,
        stream_id: int = 0,
        logger: Optional[Logger] = None,
    ):
        self.config = config
        self.output_dir = Path(output_dir)
        self.stream_id = stream_id
        self.logger = logger or Logger(f"Pipeline-{stream_id}")
        
        self.resource_monitor = ResourceMonitor()
        self.state = StreamState(stream_id=stream_id, seed=0)
        
        # In-memory storage for intermediate stage outputs
        self.stage_outputs: Dict[str, Any] = {}
        
        self.model_manager = ModelManager()
        self.device = DeviceUtils.GetDevice()
        
        PathUtils.EnsureDir(self.output_dir)
    
    def ExecuteStage(self, stage: StageConfig, seed: int) -> Optional[Any]:
        """Executes a single pipeline stage."""
        try:
            self.logger.LogInfo(f"Executing Stage: {stage.name} ({stage.type.value})")
            start_time = time.time()
            
            # Resolve input source dependency
            input_data = None
            if stage.input_source:
                if stage.input_source not in self.stage_outputs:
                    raise ValueError(f"Input source '{stage.input_source}' not found for stage '{stage.name}'")
                input_data = self.stage_outputs[stage.input_source]

            result = None
            if stage.type == StageType.TEXT_TO_IMAGE:
                result = self._HandleTextToImage(stage, seed)
            elif stage.type == StageType.IMAGE_TO_IMAGE:
                result = self._HandleImageToImage(stage, input_data, seed)
            elif stage.type == StageType.INPAINTING:
                result = self._HandleInpainting(stage, input_data, seed)
            elif stage.type == StageType.SEGMENTATION:
                result = self._HandleSegmentation(stage, input_data)
            elif stage.type == StageType.DEPTH_EXTRACTION:
                result = self._HandleDepthExtraction(stage, input_data)
            elif stage.type == StageType.BACKGROUND_REMOVAL:
                result = self._HandleBackgroundRemoval(stage, input_data)
            elif stage.type == StageType.UPSCALE:
                result = self._HandleUpscale(stage, input_data)
            else:
                self.logger.LogWarning(f"Stage type '{stage.type}' is not yet supported in this version.")

            if result is not None:
                self.stage_outputs[stage.name] = result
                
                # Persistence check
                if self.config.export.save_intermediate and isinstance(result, Image.Image):
                    output_path = self.output_dir / f"{stage.name}.png"
                    result.save(output_path)
                    self.logger.LogDebug(f"Stage result persisted: {output_path}")

            stage_time = time.time() - start_time
            self.logger.LogDebug(f"Stage '{stage.name}' metrics: {stage_time:.2f}s")
            return result

        except Exception as e:
            ErrorHandler.ReportException(e, f"SpriteGenerationPipeline.ExecuteStage({stage.name})", severity=2)
            return None

    def _HandleTextToImage(self, stage: StageConfig, seed: int) -> Image.Image:
        """Generates a base image from a text prompt."""
        self.logger.LogInfo(f"Prompt: '{stage.prompt[:60]}...'")
        
        pipe = self.model_manager.GetPipeline(
            self.config.globals.model, 
            pipeline_type="txt2img",
            quantization=self.config.globals.quantization,
            model_paths=self.config.globals.model_paths
        )
        
        generator = torch.Generator(device=self.device).manual_seed(seed)
        
        width = stage.params.get("width", 1024)
        height = stage.params.get("height", 1024)
        steps = stage.params.get("steps", 30)
        guidance_scale = stage.params.get("guidance_scale", 7.5)
        
        with torch.inference_mode():
            output = pipe(
                prompt=stage.prompt,
                negative_prompt=stage.negative_prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
        
        return output.images[0]

    def _HandleImageToImage(self, stage: StageConfig, input_data: Any, seed: int) -> Image.Image:
        """Refines or modifies an existing image based on a prompt."""
        if not isinstance(input_data, Image.Image):
            raise ValueError("Image-to-Image stage requires a PIL Image as input_source.")
        
        pipe = self.model_manager.GetPipeline(
            self.config.globals.model, 
            pipeline_type="img2img",
            quantization=self.config.globals.quantization,
            model_paths=self.config.globals.model_paths
        )
        
        generator = torch.Generator(device=self.device).manual_seed(seed)
        
        strength = stage.params.get("strength", 0.3)
        steps = stage.params.get("steps", 20)
        guidance_scale = stage.params.get("guidance_scale", 7.5)
        
        with torch.inference_mode():
            output = pipe(
                prompt=stage.prompt,
                negative_prompt=stage.negative_prompt,
                image=input_data,
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
            
        return output.images[0]

    def _HandleInpainting(self, stage: StageConfig, input_data: Any, seed: int) -> Image.Image:
        """Place-holder for inpainting logic. Currently redirects to Img2Img."""
        self.logger.LogWarning("Inpainting specialized workflow redirected to standard Img2Img refinement.")
        return self._HandleImageToImage(stage, input_data, seed)

    def _HandleSegmentation(self, stage: StageConfig, input_data: Any) -> Dict[str, Image.Image]:
        """Slices a master canvas into individual sprite parts based on LayoutConfig."""
        if not isinstance(input_data, Image.Image):
            raise ValueError("Segmentation stage requires a PIL Image as input_source.")
        
        parts = {}
        if self.config.layout:
            subfolder = stage.params.get("subfolder", "parts")
            parts_dir = PathUtils.EnsureDir(self.output_dir / subfolder)
            for part_def in self.config.layout.parts:
                # Coordinate-based cropping
                crop = input_data.crop((
                    part_def.x, 
                    part_def.y, 
                    part_def.x + part_def.width, 
                    part_def.y + part_def.height
                ))
                parts[part_def.name] = crop
                
                # Persist individual part
                part_path = parts_dir / f"{part_def.name}.png"
                crop.save(part_path)
            
            self.logger.LogInfo(f"Extracted {len(parts)} segments to {parts_dir}")
        else:
            self.logger.LogWarning("Segmentation requested but no layout configuration provided.")
            
        return parts

    def _HandleDepthExtraction(self, stage: StageConfig, input_data: Any) -> Image.Image:
        """Extracts a depth map from the input image using a pre-trained model."""
        if not isinstance(input_data, Image.Image):
            raise ValueError("Depth Extraction requires a PIL Image as input_source.")
        
        self.logger.LogInfo("Extracting depth map...")
        
        try:
            from transformers import DPTImageProcessor, DPTForDepthEstimation
            import numpy as np
            
            model_id = stage.params.get("model_id", "Intel/dpt-hybrid-midas")
            self.logger.LogDebug(f"Using depth model: {model_id}")
            
            processor = DPTImageProcessor.from_pretrained(model_id)
            model = DPTForDepthEstimation.from_pretrained(model_id).to(self.device)
            
            # Prepare image
            inputs = processor(images=input_data, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = model(**inputs)
                predicted_depth = outputs.predicted_depth
                
            # Interpolate to original size
            prediction = torch.nn.functional.interpolate(
                predicted_depth.unsqueeze(1),
                size=input_data.size[::-1],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
            
            output = prediction.cpu().numpy()
            
            # Normalize to 0-255
            depth_min = output.min()
            depth_max = output.max()
            if depth_max > depth_min:
                formatted = (255 * (output - depth_min) / (depth_max - depth_min)).astype("uint8")
            else:
                formatted = np.zeros(output.shape, dtype=np.uint8)
                
            depth_image = Image.fromarray(formatted)
            return depth_image
            
        except Exception as e:
            self.logger.LogError(f"Depth extraction failed: {e}")
            return Image.new("L", input_data.size, 128)

    def _HandleUpscale(self, stage: StageConfig, input_data: Any) -> Image.Image:
        """Upscales the input image using Lanczos resampling."""
        if not isinstance(input_data, Image.Image):
            raise ValueError("Upscale stage requires a PIL Image as input_source.")
        
        scale_factor = stage.params.get("scale_factor", 2.0)
        width, height = input_data.size
        new_size = (int(width * scale_factor), int(height * scale_factor))
        
        self.logger.LogInfo(f"Upscaling image from {input_data.size} to {new_size}...")
        
        # Using Lanczos for high quality resampling
        return input_data.resize(new_size, Image.Resampling.LANCZOS)

    def _HandleBackgroundRemoval(self, stage: StageConfig, input_data: Any) -> Image.Image:
        """Removes background from an image using rembg."""
        if not isinstance(input_data, Image.Image):
            raise ValueError("Background Removal requires a PIL Image as input_source.")
        
        self.logger.LogInfo("Removing background using rembg...")
        output = rembg.remove(input_data)
        return output

    def Generate(self, seed: int) -> Optional[PerformanceMetrics]:
        try:
            self.logger.LogInfo(f"Starting Generation Pipeline [Seed: {seed}]")
            self.resource_monitor.Start()
            self.state.seed = seed
            self.state.state = GenerationState.RUNNING
            
            start_time = time.time()
            
            for i, stage_config in enumerate(self.config.pipeline):
                self.state.current_stage_index = i
                result = self.ExecuteStage(stage_config, seed)
                
                if result is None:
                    self.state.state = GenerationState.FAILED
                    self.logger.LogError(f"Pipeline execution aborted at stage: {stage_config.name}")
                    return None
                    
                self.state.completed_stages.append(stage_config.name)
                self.resource_monitor.Update()
            
            self.state.state = GenerationState.COMPLETED
            total_time = time.time() - start_time
            
            metrics = PerformanceMetrics(
                stream_id=self.stream_id,
                seed=seed,
                peak_vram_gb=self.resource_monitor.peak_vram_gb,
                peak_ram_gb=self.resource_monitor.peak_ram_gb,
                total_parts_extracted=len(self.stage_outputs.get("segmentation", {})) if "segmentation" in self.stage_outputs else 0
            )
            
            self.logger.LogInfo(f"Generation Complete. Total Duration: {total_time:.2f}s")
            return metrics
        
        except Exception as e:
            ErrorHandler.ReportException(e, "SpriteGenerationPipeline.Generate", severity=3)
            self.state.state = GenerationState.FAILED
            return None
