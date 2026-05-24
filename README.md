# ArtSynthesis Engine

A professional, standalone sprite and character generation engine powered by SDXL and FLUX architectures. This tool provides a highly configurable pipeline for generating production-ready game assets with automatic part segmentation and metric tracking.

## Core Features
- **Configurable Pipeline**: Define generation workflows as a series of stages (txt2img, img2img, segmentation).
- **Automated Segmentation**: Extract individual sprite components based on coordinate layouts.
- **Resource Monitoring**: Real-time tracking of VRAM and RAM usage.
- **Hardware Agnostic**: Seamless execution across CUDA, MPS, and CPU devices.
- **Standalone Integrity**: Zero external project dependencies; fully self-contained logic.

## CLI Usage
```bash
# Generate assets from a configuration file
python -m artsynthesis generate --config configs/example.json --seeds 42 --streams 1 --output ./output

# Manage ongoing streams (Architectural Hooks)
python -m artsynthesis pause --stream-id 0
python -m artsynthesis resume --stream-id 0
```
