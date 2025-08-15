# generate-srt

A small Python CLI to generate SRT subtitle files from a video using ffmpeg + OpenAI's Whisper.

## Requirements

- Python 3.8+ (3.11 recommended)
- ffmpeg (in PATH)
- torch and openai-whisper (or alternate backend)

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

1. Install ffmpeg (if you don't have it):

- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg`
- Windows: download from [website](https://ffmpeg.org/download.html) and add to PATH

Verify `ffmpeg` is on your PATH:

```bash
ffmpeg -version
```

## Usage

The repository provides `main.py` which is a CLI that accepts a video path and model name. Example:

```bash
python main.py path/to/video.mp4 --model small --output subtitles.srt
```

If you omit `--output` the script writes `video_basename.srt` next to the input file.

Available model names: `tiny`, `base`, `small`, `medium`, `large`.

### Notes

- The OpenAI `whisper` Python package requires `torch` (local PyTorch) for model inference.
- If you prefer a CPU-only/fast option without PyTorch, consider `faster-whisper` with the GGML backend.
