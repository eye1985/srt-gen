# SRT generator

Requirement Windows:
- NVIDIA GPU
- CUDA Toolkit 12.x (Windows)

Requirement Mac:
- ffmpeg


Input any media file and generate a subtitle file. Transcription runs locally:
on Apple silicon via `mlx-whisper` (`whisper-large-v3`), and everywhere else
via `faster-whisper` (`large-v3` on CUDA). `ffmpeg` must be on PATH.

## Install

```sh
uv sync           # dev install into .venv
uv tool install . # or install the CLI globally
```

## Usage

```sh
srt-gen --input ./videos/video01.mp4 --language en
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--input` | yes | — | Path to the media file, eg. `./videos/video01.mp4` |
| `--language` | no | `en` | ISO 639-1 code of the spoken media, see [Languages](#languages) |

There is no `--output` flag. The `.srt` is written next to the input file,
reusing its base name (`./videos/video01.mp4` → `./videos/video01.srt`).

## Languages

`--language` is passed straight to the Whisper backend and must be the exact
**ISO 639-1 code** (`no`, not `Norwegian` or `NO`) — `faster-whisper` (used on
CUDA) validates it against the code list only and rejects anything else,
including language names and case variants.

`whisper-large-v3` supports 100 languages:

| Code | Name | Code | Name |
| --- | --- | --- | --- |
| `af` | afrikaans | `lv` | latvian |
| `am` | amharic | `mg` | malagasy |
| `ar` | arabic | `mi` | maori |
| `as` | assamese | `mk` | macedonian |
| `az` | azerbaijani | `ml` | malayalam |
| `ba` | bashkir | `mn` | mongolian |
| `be` | belarusian | `mr` | marathi |
| `bg` | bulgarian | `ms` | malay |
| `bn` | bengali | `mt` | maltese |
| `bo` | tibetan | `my` | myanmar |
| `br` | breton | `ne` | nepali |
| `bs` | bosnian | `nl` | dutch |
| `ca` | catalan | `nn` | nynorsk |
| `cs` | czech | `no` | norwegian |
| `cy` | welsh | `oc` | occitan |
| `da` | danish | `pa` | punjabi |
| `de` | german | `pl` | polish |
| `el` | greek | `ps` | pashto |
| `en` | english | `pt` | portuguese |
| `es` | spanish | `ro` | romanian |
| `et` | estonian | `ru` | russian |
| `eu` | basque | `sa` | sanskrit |
| `fa` | persian | `sd` | sindhi |
| `fi` | finnish | `si` | sinhala |
| `fo` | faroese | `sk` | slovak |
| `fr` | french | `sl` | slovenian |
| `gl` | galician | `sn` | shona |
| `gu` | gujarati | `so` | somali |
| `ha` | hausa | `sq` | albanian |
| `haw` | hawaiian | `sr` | serbian |
| `he` | hebrew | `su` | sundanese |
| `hi` | hindi | `sv` | swedish |
| `hr` | croatian | `sw` | swahili |
| `ht` | haitian creole | `ta` | tamil |
| `hu` | hungarian | `te` | telugu |
| `hy` | armenian | `tg` | tajik |
| `id` | indonesian | `th` | thai |
| `is` | icelandic | `tk` | turkmen |
| `it` | italian | `tl` | tagalog |
| `ja` | japanese | `tr` | turkish |
| `jw` | javanese | `tt` | tatar |
| `ka` | georgian | `uk` | ukrainian |
| `kk` | kazakh | `ur` | urdu |
| `km` | khmer | `uz` | uzbek |
| `kn` | kannada | `vi` | vietnamese |
| `ko` | korean | `yi` | yiddish |
| `la` | latin | `yo` | yoruba |
| `lb` | luxembourgish | `yue` | cantonese |
| `ln` | lingala | `zh` | chinese |
| `lo` | lao | | |
| `lt` | lithuanian | | |

`yue` (cantonese) is exclusive to `large-v3`; older Whisper models only know the
other 99.

## Library

```python
from srt_gen.whisper import whisper_transcribe
from srt_gen.writer import write_to

texts = whisper_transcribe("video01.mp4", "en")
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
