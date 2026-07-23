# SRT generator

Requirement Windows:
- NVIDIA GPU
- CUDA Toolkit 12.x (Windows)

Requirement Mac:
- ffmpeg


Input any media file and generate a subtitle file. Transcription runs locally.

**Only two platforms are supported:** 
 - **Apple silicon**
 - **NVIDIA GPUs with CUDA.**

Any other hardware (e.g. CPU-only, AMD, Intel GPUs) is not supported and the
CLI will exit with an error. On Apple silicon transcription runs via
`mlx-whisper` (`whisper-large-v3`); on NVIDIA/CUDA it runs via
`faster-whisper` (`large-v3`).

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
| `--language` | no | auto-detect | ISO 639-1 code of the spoken media, see [Languages](#languages) |
| `--translate` | no | off | Output English subtitles instead of the spoken language, see [Translation](#translation) |

There is no `--output` flag. The `.srt` is written next to the input file,
reusing its base name (`./videos/video01.mp4` → `./videos/video01.srt`).

Omitting `--language` lets Whisper detect the spoken language from the first 30
seconds of audio. That is usually right, but a file that opens with music,
silence or a different language than the body can be misdetected — pass
`--language` explicitly when you already know it.

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

## Translation

```sh
srt-gen --input ./videos/norsk.mp4 --language no --translate
```

`--translate` switches the backend from Whisper's `transcribe` task to its
`translate` task (`task="translate"` on both `mlx-whisper` and
`faster-whisper`). `--language` still describes the **spoken** audio; it is the
source, not the target.

Some caveats worth knowing before relying on it:

- **English is the only target.** This is a single mode the model was trained
  with, not a general translator — there is no option for any other output
  language. Norwegian → English works; Norwegian → German does not.
- **Quality is well below a dedicated translator.** Translation is a side
  capability of a speech recognition model, so expect literal phrasing, dropped
  nuance and occasional mistranslated idioms or names. For anything that has to
  be accurate, transcribe in the source language and run the `.srt` through a
  real translation step.
- **Timings get looser.** `mlx-whisper` warns that word-level timestamps are
  unreliable on translations, since translated text no longer lines up
  one-to-one with the audio it came from. Subtitle timings are taken per
  segment, which holds up better, but drift is still more likely than on a
  plain transcription.

Without the flag the subtitles stay in the spoken language.

## Library

```python
from srt_gen.whisper import whisper_transcribe
from srt_gen.writer import write_to

texts = whisper_transcribe("video01.mp4", "en")
write_to("video01.srt", texts, srt=True)
```

Both `whisper_transcribe` (Apple silicon) and `faster_whisper_transcribe`
(CUDA) take the same `(file_path, language, translate=False)` arguments. Pass
`language=None` to auto-detect, `translate=True` to get English out.

## Layout

```
src/srt_gen/
  main.py      argparse entry point (srt-gen)
  languages.py supported language codes
  whisper.py   mlx-whisper + faster-whisper transcription
  writer.py    SRT / plain-text output
  speech.py    TTS via mlx-audio (lazy model load)
  utils.py     platform + timestamp helpers
```
