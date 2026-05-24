import torch
import psutil
from typing import Optional


class DeviceUtils:
    @staticmethod
    def GetDevice() -> torch.device:
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            return torch.device("mps")
        else:
            return torch.device("cpu")
    
    @staticmethod
    def GetAvailableVRAM() -> float:
        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        return 0.0
    
    @staticmethod
    def GetPeakVRAMUsage() -> float:
        if torch.cuda.is_available():
            return torch.cuda.max_memory_allocated() / (1024 ** 3)
        return 0.0
    
    @staticmethod
    def GetSystemRAM() -> float:
        return psutil.virtual_memory().total / (1024 ** 3)
    
    @staticmethod
    def GetAvailableSystemRAM() -> float:
        return psutil.virtual_memory().available / (1024 ** 3)
    
    @staticmethod
    def PrintDeviceInfo() -> None:
        device = DeviceUtils.GetDevice()
        print(f"Device: {device}")
        
        if device.type == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {DeviceUtils.GetAvailableVRAM():.1f} GB")
        
        print(f"System RAM: {DeviceUtils.GetSystemRAM():.1f} GB ({DeviceUtils.GetAvailableSystemRAM():.1f} GB available)")
