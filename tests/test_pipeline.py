import unittest
from pathlib import Path
from PIL import Image
import numpy as np
from tools.ArtGeneration.ConfigLoader import ConfigLoader
from tools.ArtGeneration.CharacterPartSetGenerator import CharacterPartSetGenerator
from tools.ArtGeneration.DepthMapGenerator import DepthMapGenerator
from tools.ArtGeneration.ControlNetPipeline import ControlNetPipeline

class TestArtGenerationPipeline(unittest.TestCase):

    def setUp(self):
        """Set up test environment."""
        self.config_path = Path('tools/ArtGeneration/configs/character_military_engineer.json')
        self.output_dir = Path('tools/ArtGeneration/Output/test_output')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.config = ConfigLoader.load(self.config_path)
        self.silhouette_path = self.output_dir / 'silhouette.png'
        self.depth_map_path = self.output_dir / 'depth_map.png'

    def test_silhouette_generation(self):
        """Test silhouette generation."""
        from tools.ArtGeneration.RealisticCharacterGenerator import RealisticCharacterGenerator
        generator = RealisticCharacterGenerator()
        silhouette = generator._synthesize_silhouette(self.config, self.config.resolution, debug=True)
        silhouette.save(self.silhouette_path)
        self.assertTrue(self.silhouette_path.exists(), "Silhouette file was not created.")

    def test_depth_map_generation(self):
        """Test depth map generation."""
        silhouette = Image.open(self.silhouette_path).convert("L")
        depth_map = DepthMapGenerator.create_from_silhouette(silhouette, self.config.resolution)
        depth_map.save(self.depth_map_path)
        self.assertTrue(self.depth_map_path.exists(), "Depth map file was not created.")
        self.assertEqual(depth_map.size, (self.config.resolution, self.config.resolution), "Depth map resolution mismatch.")

    def test_character_parts_generation(self):
        """Test character parts generation."""
        generator = CharacterPartSetGenerator()
        generator.generate_from_silhouette(self.config, self.silhouette_path, self.output_dir)
        parts_dir = self.output_dir / 'parts'
        self.assertTrue(parts_dir.exists(), "Parts directory was not created.")
        self.assertGreater(len(list(parts_dir.glob('*.png'))), 0, "No parts were generated.")

if __name__ == "__main__":
    unittest.main()