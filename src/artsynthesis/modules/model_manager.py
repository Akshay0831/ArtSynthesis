import torch
from pathlib import Path
from typing import Optional, Union, Dict, Any
from diffusers import (
    StableDiffusionXLPipeline, 
    StableDiffusionXLImg2ImgPipeline,
    FluxPipeline,
)
from artsynthesis.config import ModelType, QuantizationType
from artsynthesis.utils import Logger, DeviceUtils


class ModelManager:
    """Manages loading and caching of diffusion models."""
    
    _instance = None
    _models: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, 'initialized'):
            return
            
        self.logger = Logger("ModelManager")
        self.device = DeviceUtils.GetDevice()
        self.initialized = True
        
    def GetPipeline(
        self, 
        model_type: ModelType, 
        pipeline_type: str = "txt2img",
        quantization: QuantizationType = QuantizationType.NONE,
        model_paths: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Retrieves or loads a diffusion pipeline based on configuration.
        """
        cache_key = f"{model_type.value}_{pipeline_type}_{quantization.value}"
        
        if cache_key in self._models:
            return self._models[cache_key]
        
        self.logger.LogInfo(f"Loading pipeline: {cache_key}")
        
        # Resolve model path from configuration mapping
        model_path_str = (model_paths or {}).get(model_type.value)
        if not model_path_str:
            raise ValueError(f"No model path configured for model type: {model_type.value}")
            
        model_path = Path(model_path_str).resolve()
        if not model_path.exists():
            raise FileNotFoundError(f"Model weights not found at configured path: {model_path}")

        try:
            pipeline = None
            if model_type == ModelType.SDXL:
                loading_args = {
                    "pretrained_model_name_or_path": model_path,
                    "torch_dtype": torch.float16 if self.device.type == "cuda" else torch.float32,
                    "use_safetensors": True,
                }
                
                if pipeline_type == "txt2img":
                    pipeline = StableDiffusionXLPipeline.from_pretrained(**loading_args)
                elif pipeline_type == "img2img":
                    pipeline = StableDiffusionXLImg2ImgPipeline.from_pretrained(**loading_args)

            elif model_type == ModelType.FLUX:
                dtype = torch.bfloat16 if self.device.type == "cuda" else torch.float32
                pipeline = FluxPipeline.from_pretrained(
                    model_path, 
                    torch_dtype=dtype,
                    use_safetensors=True
                )

            if pipeline:
                pipeline.to(self.device)
                self._ApplyMemoryOptimizations(pipeline, model_type)
                self._models[cache_key] = pipeline
                return pipeline
            
            raise ValueError(f"Unsupported pipeline configuration: {pipeline_type} for {model_type.value}")
            
        except Exception as e:
            self.logger.LogError(f"Failed to initialize pipeline {cache_key}: {e}")
            raise

    def _ApplyMemoryOptimizations(self, pipeline: Any, model_type: ModelType) -> None:
        """Applies hardware-specific memory optimizations to the pipeline."""
        if self.device.type != "cuda":
            return

        try:
            if model_type == ModelType.SDXL:
                pipeline.enable_xformers_memory_efficient_attention()
            elif model_type == ModelType.FLUX:
                pipeline.enable_model_cpu_offload()
        except Exception as e:
            self.logger.LogWarning(f"Memory optimization failed: {e}")

    def ClearCache(self):
        """Evicts all models from memory and clears VRAM."""
        self._models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
