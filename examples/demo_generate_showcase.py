from pathlib import Path
from PIL import Image, ImageDraw
from typing import Optional
from pixelart.core.design_engine import TextureMapFromSpriteGenerator, SpriteBackgroundTransparencyProcessor
from pixelart.rendering import SpriteCompositionVisualizer
from pixelart.config.multipart_config import MultipartConfig, BOSS_CONFIG


def _trim_transparent_border(img: Image.Image, pad: int = 4) -> Image.Image:
    bbox = img.getbbox()
    if bbox is None:
        return img
    left, upper, right, lower = bbox
    left = max(0, left - pad)
    upper = max(0, upper - pad)
    right = min(img.width, right + pad)
    lower = min(img.height, lower + pad)
    return img.crop((left, upper, right, lower))


def make_part(name: str, size, color, out_dir: Path, sprite_id: str) -> Path:
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if name == "Head":
        draw.ellipse([(w * 0.15, h * 0.05), (w * 0.85, h * 0.75)], fill=color + (255,))
        draw.ellipse([(w * 0.45, h * 0.3), (w * 0.6, h * 0.45)], fill=(255, 255, 255, 120))
    elif name == "Torso" or name == "Body" or name == "Chassis":
        draw.rounded_rectangle([(w * 0.05, h * 0.05), (w * 0.95, h * 0.95)], radius=12, fill=color + (255,))
    elif name in ("Arm_Left", "Arm_Right", "Arm"):
        draw.rectangle([(w * 0.15, h * 0.1), (w * 0.85, h * 0.9)], fill=color + (255,))
    elif name in ("Leg_Left", "Leg_Right", "Leg"):
        draw.rectangle([(w * 0.2, h * 0.05), (w * 0.8, h * 0.95)], fill=color + (255,))
    elif name in ("Wheel_Left", "Wheel_Right"):
        draw.ellipse([(w * 0.1, h * 0.1), (w * 0.9, h * 0.9)], fill=color + (255,))
    elif name in ("Wing_Left", "Wing_Right"):
        points = [(w * 0.1, h * 0.5), (w * 0.9, h * 0.2), (w * 0.9, h * 0.8)]
        draw.polygon(points, fill=color + (255,))
    else:
        draw.polygon([(w * 0.5, h * 0.05), (w * 0.9, h * 0.9), (w * 0.1, h * 0.9)], fill=color + (255,))

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{sprite_id}_{name}_Base.png"
    img = _trim_transparent_border(img, pad=2)
    img.save(path)
    return path


def run_demo(config: Optional[MultipartConfig] = None, output_root: Optional[Path] = None, sprite_id: Optional[str] = None) -> Path:
    if config is None:
        config = BOSS_CONFIG
    if output_root is None:
        output_root = Path(__file__).parent / "Output" / f"Demo{config.sprite_type}"
    if sprite_id is None:
        sprite_id = f"Demo{config.sprite_type}"
    
    output_root.mkdir(parents=True, exist_ok=True)
    generated = {}
    
    for part_name in config.parts:
        part_dir = output_root / part_name
        
        size = config.part_sizes.get(part_name, (100, 100)) if config.part_sizes else (100, 100)
        color = config.part_colors.get(part_name, (128, 128, 128)) if config.part_colors else (128, 128, 128)
        
        p = make_part(part_name, size, color, part_dir, sprite_id)
        SpriteBackgroundTransparencyProcessor.apply_alpha_transparency_to_background(p)
        processed = Image.open(p).convert("RGBA")
        processed = _trim_transparent_border(processed, pad=2)
        processed.save(p)
        generated[part_name] = p
        
        TextureMapFromSpriteGenerator.auto_generate_all_texture_maps(part_dir)

    visualizer = SpriteCompositionVisualizer((512, 512))
    preview = visualizer.compose_from_parts(
        parts_dict=generated,
        config=config,
        lighting_angle=45,
        ambient_brightness=1.0
    )
    preview_path = output_root / f"Demo{config.sprite_type}_Preview.png"
    preview.save(preview_path)
    print(f"Demo generated: {output_root} (preview: {preview_path})")
    
    return output_root


if __name__ == "__main__":
    run_demo()
