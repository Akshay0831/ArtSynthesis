from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import json


@dataclass
class ReferenceMaterial:
    name: str
    category: str
    path: str
    description: str = ""
    tags: list[str] = None


@dataclass
class ReferenceSearchConfig:
    enable_search: bool = True
    index_path: str = "./references"


class ReferenceMaterialSearch:
    def __init__(self, config: ReferenceSearchConfig = None):
        self.config = config or ReferenceSearchConfig()
        self.index_path = Path(self.config.index_path)
        self.materials: list[ReferenceMaterial] = []
        
        if self.IsEnabled():
            self.IndexMaterials()
    
    def IsEnabled(self) -> bool:
        return self.config.enable_search
    
    def IndexMaterials(self) -> None:
        if not self.index_path.exists():
            return
        
        for file in self.index_path.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                
                material = ReferenceMaterial(
                    name=data.get("name", ""),
                    category=data.get("category", ""),
                    path=data.get("path", ""),
                    description=data.get("description", ""),
                    tags=data.get("tags", []),
                )
                
                self.materials.append(material)
            except (json.JSONDecodeError, KeyError):
                continue
    
    def Search(self, query: str, category: Optional[str] = None) -> list[ReferenceMaterial]:
        query_lower = query.lower()
        results = []
        
        for material in self.materials:
            if category and material.category != category:
                continue
            
            if query_lower in material.name.lower():
                results.append(material)
            elif any(query_lower in tag.lower() for tag in material.tags):
                results.append(material)
        
        return results
    
    def GetStyleGuides(self, asset_type: str) -> list[ReferenceMaterial]:
        return self.Search(asset_type, category="style")
