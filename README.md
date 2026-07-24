# SRT generator

Input any media file and generate a subtitle file. Transcription runs locally.

Only two platforms are supported:

- **Apple silicon** (M1 or newer) — runs `mlx-whisper` (`whisper-large-v3`)
- **Windows + NVIDIA GPU** — runs `faster-whisper` (`large-v3`)

No external toolchain is required on either. The CUDA runtime (cuBLAS + cuDNN)
ships as pip wheels, so on Windows you only need a current **NVIDIA driver** —
**not** the CUDA Toolkit. 

**Linux is not supported**; the CLI exits.

## Install

Requires **Python 3.11+**. The Apple-silicon and Windows/CUDA dependency sets
are selected by standard environment markers, so any installer works — the
examples below use **[uv](https://docs.astral.sh/uv/)**, which fetches a suitable
Python for you if you do not have one.

```sh
uv tool install git+https://github.com/eye1985/srt-gen
srt-gen --input ./videos/video01.mp4 --language en
```

To uninstall:

```sh
uv tool uninstall srt-gen
```

No clone or manual Python install needed. To work on the project instead:

```sh
git clone https://github.com/eye1985/srt-gen.git
cd srt-gen

uv sync   # creates .venv, run with `uv run srt-gen ...`
```

## Usage

```sh
srt-gen --input ./videos/video01.mp4 --language en
```

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--input` | yes | — | Path to the media file, eg. `./videos/video01.mp4` |
| `--language` | no | auto-detect | ISO 639-1 code of the spoken media, see [Languages](#languages) |
| `--translate` | no | off | Output English subtitles instead of the spoken language, see [Translation](#translation) |

There is no `--output` flag. The `.srt` is written next to the input file,
reusing its base name (`./videos/video01.mp4` → `./videos/video01.srt`).

Omitting `--language` detects the language from the first 30 seconds, which can
misfire on files that open with music, silence or another language.

## Languages

`--language` must be the exact **ISO 639-1 code** (`no`, not `Norwegian` or
`NO`). `whisper-large-v3` supports 100 languages:

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

## Translation

```sh
srt-gen --input ./videos/norsk.mp4 --language no --translate
```

`--language` still describes the **spoken** audio; it is the source, not the
target.

- **English is the only target.** Norwegian → English works; Norwegian →
  German does not.
- **Quality is below a dedicated translator.** Expect literal phrasing and
  occasional mistranslated idioms or names.
- **Timings get looser** than on a plain transcription.

## Library

```python
from srt_gen.whisper import whisper_transcribe
from srt_gen.writer import write_to

texts = whisper_transcribe("video01.mp4", "en")
write_to("video01.srt", texts, srt=True)
```

Both `whisper_transcribe` (Apple silicon) and `faster_whisper_transcribe`
(Windows + NVIDIA) take `(file_path, language, translate=False)`. Pass
`language=None` to auto-detect, `translate=True` to get English out.

## Layout

```
src/srt_gen/
  main.py      argparse entry point (srt-gen)
  languages.py supported language codes
  whisper.py   mlx-whisper + faster-whisper transcription
  writer.py    SRT / plain-text output
  utils.py     platform + timestamp helpers
```
