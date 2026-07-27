# SRT generator

Input any media file and generate a subtitle file. Transcription runs locally.

Only two platforms are supported:

- **Apple silicon** (M1 or newer) — runs `mlx-whisper` (`whisper-large-v3` by default)
- **Windows + NVIDIA GPU** — runs `faster-whisper` (`large-v3` by default)

The model is configurable with `--model`, see [Models](#models).

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
| `--model` | no | `large-v3` | Model to transcribe with, see [Models](#models) |
| `--language` | no | auto-detect | ISO 639-1 code of the spoken media, see [Languages](#languages) |
| `--translate` | no | off | Output English subtitles instead of the spoken language, see [Translation](#translation) |
| `--temperature` | no | `0.8` | Decoding temperature; `0.0` is greedy, see [Decoding](#decoding) |
| `--condition-on-previous-text` | no | off | Feed each segment the previous one as context, see [Decoding](#decoding) |
| `--ui` | no | off | Open the desktop window instead of transcribing, see [UI](#ui) |

There is no `--output` flag. The `.srt` is written next to the input file,
reusing its base name (`./videos/video01.mp4` → `./videos/video01.srt`).

Omitting `--language` detects the language from the first 30 seconds, which can
misfire on files that open with music, silence or another language.

## Decoding

`--temperature` controls how much the decoder is allowed to wander. `0.0` is
greedy — it always takes the most likely token, which is the steadiest choice
and the best one on Apple silicon, where there is no beam search to fall back
on. Higher values let it consider less likely tokens, which sometimes recovers
from a bad patch of audio and sometimes invents text that was never spoken.

`--condition-on-previous-text` feeds each segment the previous segment as
context. It reads better on continuous speech, because the model keeps names and
terminology consistent across segment boundaries. The tradeoff is that a single
bad segment can poison everything after it — the model repeats or loops on its
own mistake. It is off by default for that reason; turn it on for clean,
continuous audio.

## UI

```sh
srt-gen --ui
```

Opens a desktop window: pick a file, set the options, watch the log and progress
bar as it decodes. The `.srt` is written next to the input exactly as it is on
the command line.

`--ui` is checked before anything else, so it ignores every other flag —
`srt-gen --ui --input x.mp4` opens the window with no file selected. Set the
options in the window instead.

The window exposes model, auto-detect language, language, temperature, condition
on previous text, and translate. **It runs on Apple silicon only** — on
Windows + NVIDIA the window opens, but starting a transcription fails. Use the
command line there.

## Models

The model set depends on your platform — Apple silicon loads `mlx-whisper`
weights, Windows/NVIDIA loads `faster-whisper` weights. Pass the exact name from
the column for your platform. Omitting `--model` uses the default (**bold**).
Unrecognised names are rejected and the CLI prints the supported list.

Larger models are more accurate but slower; `.en` variants are English-only (do
not use them with a non-English `--language`); `turbo`/`distil` trade a little
accuracy for speed. Weights are downloaded on first use and cached.

| Apple silicon (`mlx-whisper`) | Windows + NVIDIA (`faster-whisper`) |
| --- | --- |
| `mlx-community/whisper-tiny-mlx` | `tiny` |
| `mlx-community/whisper-tiny.en-mlx` | `tiny.en` |
| `mlx-community/whisper-base-mlx` | `base` |
| `mlx-community/whisper-base.en-mlx` | `base.en` |
| `mlx-community/whisper-small-mlx` | `small` |
| `mlx-community/whisper-small.en-mlx` | `small.en` |
| `mlx-community/whisper-medium-mlx` | `medium` |
| `mlx-community/whisper-medium.en-mlx` | `medium.en` |
| `mlx-community/whisper-large-mlx` | `large` |
| `mlx-community/whisper-large-v1-mlx` | `large-v1` |
| `mlx-community/whisper-large-v2-mlx` | `large-v2` |
| **`mlx-community/whisper-large-v3-mlx`** | **`large-v3`** |
| `mlx-community/whisper-large-v3-turbo` | `large-v3-turbo` |
| — | `turbo` |
| `mlx-community/distil-whisper-medium.en` | `distil-medium.en` |
| `mlx-community/distil-whisper-large-v3` | `distil-large-v3` |
| — | `distil-small.en` |
| — | `distil-large-v2` |
| — | `distil-large-v3.5` |

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

texts = whisper_transcribe("video01.mp4", "en", "")
write_to("video01.srt", texts, srt=True)
```

Both `whisper_transcribe` (Apple silicon) and `faster_whisper_transcribe`
(Windows + NVIDIA) take:

```python
(file_path, language, model, translate=False, temperature=..., 
 condition_on_previous_text=False, on_progress=None)
```

Pass `language=None` to auto-detect, an empty `model` (`""`) to use the platform
default, and `translate=True` to get English out. An unsupported `model` raises
`NotSupportedModelException`.

`temperature` defaults to `0.0` on `whisper_transcribe` (greedy — mlx has no
beam search) and `0.8` on `faster_whisper_transcribe`. Note that the `srt-gen`
command passes `0.8` to both, so calling the library directly on Apple silicon
without an explicit `temperature` decodes differently than the CLI does.

`on_progress` is called with the fraction decoded so far, `0.0` → `1.0`.

## Layout

```
src/srt_gen/
  main.py      entry point (srt-gen): picks backend, writes output
  cli.py       argparse flag definitions
  languages.py supported language codes
  models.py    per-platform model lists and defaults
  whisper.py   mlx-whisper + faster-whisper transcription
  writer.py    SRT / plain-text output
  utils.py     platform + timestamp helpers
  ui/
    app.py                 main window (--ui)
    transcribe_options.py  the options form
    transcribe_worker.py   runs the transcription off the GUI thread
    log_stream.py          pipes backend stdout into the log panel
```
