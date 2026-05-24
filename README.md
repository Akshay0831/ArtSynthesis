# ArtSynthesis

Professional stand-alone art generation engine using SDXL and FLUX.
Modular, feature-based architecture controlled by flexible options.

## Features
- Multi-stream generation
- Modular part extraction
- Checkpoint and metrics tracking
- Device-agnostic (CUDA/CPU)
- Fully configurable via YAML/JSON

## Installation
```bash
pip install -e .
```

## Usage
```bash
python -m artsynthesis --config configs/example.yaml --generate
```
