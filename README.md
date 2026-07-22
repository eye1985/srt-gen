# SRT generator

Requirement Windows:
- NVIDIA GPU
- CUDA Toolkit 12.x (Windows)

Requirement Mac:
- ffmpeg


Input any media file and generate a subtitle file. Transcription runs locally
via `mlx-whisper` (`whisper-large-v3`), so it currently requires Apple silicon
and `ffmpeg` on PATH.

## Install

```sh
uv sync           # dev install into .venv
uv tool install . # or install the CLI globally
```

## Usage

```sh
srt-gen --input ./videos/video01.mp4 --language english
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--input` | yes | — | Path to the media file, eg. `./videos/video01.mp4` |
| `--language` | no | `english` | Spoken language of the media, see [Languages](#languages) |

There is no `--output` flag. The `.srt` is written next to the input file,
reusing its base name (`./videos/video01.mp4` → `./videos/video01.srt`).

## Languages

`--language` is passed straight to the Whisper tokenizer. It accepts either the
**ISO 639-1 code** or the **English name** of the language, and matching is
case-insensitive (`NO`, `no`, `Norwegian` and `norwegian` all work the same).
Anything else fails with `Unsupported language: ...`.

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

### Alternative names

These extra spellings are accepted as aliases and resolve to the code shown:

| Alias | Resolves to |
| --- | --- |
| `burmese` | `my` (myanmar) |
| `castilian` | `es` (spanish) |
| `flemish` | `nl` (dutch) |
| `haitian` | `ht` (haitian creole) |
| `letzeburgesch` | `lb` (luxembourgish) |
| `mandarin` | `zh` (chinese) |
| `moldavian` | `ro` (romanian) |
| `moldovan` | `ro` (romanian) |
| `panjabi` | `pa` (punjabi) |
| `pushto` | `ps` (pashto) |
| `sinhalese` | `si` (sinhala) |
| `valencian` | `ca` (catalan) |

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
