# SRT generator

In development

Input any media file and generate a subtitle file. Transcription runs locally
via `mlx-whisper`, so it currently requires Apple silicon and `ffmpeg` on PATH.

## Install

```sh
uv sync           # dev install into .venv
uv tool install . # or install the CLI globally
```

## Usage

```sh
srt-gen --input ./videos/video01.mp4 --output ./results/video01.srt --language english
```

`--language` defaults to `english`.

## Library

```python
from srt_gen.whisper import whisper_transcribe
from srt_gen.writer import write_to

texts = whisper_transcribe("video01.mp4", "english")
write_to("video01.srt", texts, srt=True)
```

## Layout

```
src/srt_gen/
  main.py      argparse entry point (srt-gen)
  whisper.py   mlx-whisper transcription
  writer.py    SRT / plain-text output
  speech.py    TTS via mlx-audio (lazy model load)
  utils.py     platform + timestamp helpers
```