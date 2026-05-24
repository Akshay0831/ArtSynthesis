from pathlib import Path
from typing import Union


class PathUtils:
    @staticmethod
    def ResolvePath(path: Union[str, Path], base_dir: Union[str, Path] = None) -> Path:
        path = Path(path)
        
        if path.is_absolute():
            return path
        
        if base_dir is None:
            return path.resolve()
        
        base_dir = Path(base_dir)
        if base_dir.is_dir():
            return (base_dir / path).resolve()
        else:
            return (base_dir.parent / path).resolve()
    
    @staticmethod
    def EnsureDir(dir_path: Union[str, Path]) -> Path:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def GetRelativePath(target: Union[str, Path], base: Union[str, Path]) -> Path:
        target = Path(target).resolve()
        base = Path(base).resolve()
        
        try:
            return target.relative_to(base)
        except ValueError:
            return target
