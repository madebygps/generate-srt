from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from typing import List


def run_ffmpeg_extract_audio(video_path: str, out_audio: str) -> None:
    """Extract audio from video using ffmpeg into a WAV file (16kHz mono)."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-vn",
        out_audio,
    ]
    print("Running:", " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except FileNotFoundError:
        raise FileNotFoundError(
            "ffmpeg not found. Install ffmpeg (macOS: `brew install ffmpeg`) and ensure it's on your PATH."
        )


def format_timestamp(seconds: float) -> str:
    """Format seconds to SRT timestamp: HH:MM:SS,mmm"""
    millis = int(round(seconds * 1000))
    hours = millis // (3600 * 1000)
    millis -= hours * 3600 * 1000
    minutes = millis // (60 * 1000)
    millis -= minutes * 60 * 1000
    secs = millis // 1000
    millis -= secs * 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def segments_to_srt(segments: List[dict]) -> str:
    """Convert whisper-style segments to SRT formatted text."""
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg.get("text", "").strip()
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)


def transcribe_audio_whisper(audio_path: str, model: str = "small") -> List[dict]:
    try:
        import whisper
    except Exception:
        print("Failed to import whisper.")
        raise

    print(f"Loading model '{model}' (this may take a while)...")
    m = whisper.load_model(model)



    # Using whisper.transcribe which returns segments in the result when 'word_timestamps' is not needed
    print("Transcribing audio...")
    result = m.transcribe(audio_path)

    # Validate the structure returned by the model. Some implementations or
    # unexpected results may return non-list values for 'segments'. Ensure we
    # always return a List[dict].
    segments_candidate = []
    if isinstance(result, dict):
        sc = result.get("segments")
        if isinstance(sc, list):
            segments_candidate = sc

    if not segments_candidate:
        # fallback: create single segment when segments aren't available
        print("No segments returned by model, creating single-segment output.")
        if isinstance(result, dict):
            duration = result.get("duration", 0.0)
            text = result.get("text", "")
        else:
            duration = 0.0
            text = ""

        # Coerce duration to float safely
        safe_duration = 0.0
        if isinstance(duration, (int, float)):
            safe_duration = float(duration)
        elif isinstance(duration, str):
            try:
                safe_duration = float(duration)
            except ValueError:
                safe_duration = 0.0

        return [{"start": 0.0, "end": safe_duration, "text": text}]

    return segments_candidate


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate SRT subtitles from a video file"
    )
    parser.add_argument("input", help="Path to input video file")
    parser.add_argument(
        "--model",
        default="small",
        help="Whisper model name (tiny, base, small, medium, large)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output SRT file path (defaults to same name as input) ",
    )
    args = parser.parse_args(argv)

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"Input file not found: {input_path}")
        return 2

    output_srt = args.output or os.path.splitext(input_path)[0] + ".srt"

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")
        try:
            run_ffmpeg_extract_audio(input_path, audio_path)
        except subprocess.CalledProcessError:
            print(
                "ffmpeg failed. Make sure ffmpeg is installed and the input file is valid."
            )
            return 3

        segments = transcribe_audio_whisper(audio_path, model=args.model)

    srt_text = segments_to_srt(segments)

    with open(output_srt, "w", encoding="utf-8") as f:
        f.write(srt_text)

    print(f"Wrote SRT to: {output_srt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
