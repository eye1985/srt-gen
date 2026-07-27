import time
from contextlib import contextmanager
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from importlib import import_module
from types import SimpleNamespace
from typing import Callable, Optional, TypedDict
from .utils import add_cuda_dll_dirs, to_hh_mm_ss_ms
from .models import mlx_default_model, mlx_models, fw_default_model, fw_models

WhisperResult = TypedDict(
    "WhisperResult",
    {
        "start": float,
        "end": float,
        "text": str,
    },
)

# Called with the fraction of audio decoded so far, 0.0 -> 1.0.
ProgressCallback = Callable[[float], None]


class _ProgressBar:
    """Stands in for a tqdm bar so its frame counter becomes a callback instead."""

    def __init__(self, on_progress: ProgressCallback, total: int = 0, **_kwargs):
        self.total = total
        self.n = 0
        self._on_progress = on_progress

    def update(self, n: int):
        self.n += n
        if self.total > 0:
            self._on_progress(min(self.n / self.total, 1.0))

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        return False


@contextmanager
def _mlx_progress(on_progress: Optional[ProgressCallback]):
    """Swap the tqdm mlx_whisper decodes with, so we can observe its frame counter.

    mlx_whisper.transcribe() exposes no progress hook and only returns once the whole
    file is done, but it does tick a tqdm bar (total=content_frames) after every decoded
    window. Substituting the bar is the only way to see that progress from the outside.
    """
    if on_progress is None:
        yield
        return

    # import_module, not `import mlx_whisper.transcribe`: the package re-exports a
    # transcribe() function under that same name, which shadows the module.
    mlx_transcribe = import_module("mlx_whisper.transcribe")

    original = mlx_transcribe.tqdm
    mlx_transcribe.tqdm = SimpleNamespace(
        tqdm=lambda **kwargs: _ProgressBar(on_progress, **kwargs)
    )
    try:
        yield
    finally:
        mlx_transcribe.tqdm = original


class NotSupportedModelException(Exception):
    pass


NOT_SUPPORTED_MODEL_MESSAGE = "Please pick a model from the supported list."


def whisper_transcribe(
    file_path: str,
    language,
    model: str,
    translate: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> list[WhisperResult]:
    model = model or mlx_default_model
    if model not in mlx_models:
        raise NotSupportedModelException(NOT_SUPPORTED_MODEL_MESSAGE)

    import mlx_whisper  # only importable/usable on Apple Silicon (Metal-based)

    if language is None:
        print("Language not specified, will use auto detection")

    start_time = time.perf_counter()

    task = "translate" if translate else "transcribe"

    # mlx_whisper.transcribe() would otherwise shell out to an `ffmpeg` binary to
    # decode. PyAV (a faster-whisper dependency) has ffmpeg linked into its wheel,
    # so decoding here keeps the CLI free of any external install.
    audio = decode_audio(file_path, sampling_rate=16000)

    with _mlx_progress(on_progress):
        output = mlx_whisper.transcribe(
            audio,
            path_or_hf_repo=model,
            word_timestamps=True,
            language=language,
            task=task,
            temperature=0.0,  # greedy; mlx has no beam search, so 0 is best quality
            condition_on_previous_text=False,
            verbose=True,  # print each segment as it's decoded (True) / progress bar (False)
        )

    segments = output["segments"]
    texts = list(
        map(
            lambda x: {"start": x["start"], "end": x["end"], "text": x["text"].strip()},
            segments,
        )
    )

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("Transcribe complete in %s" % (to_hh_mm_ss_ms(elapsed_time)))

    return texts


def faster_whisper_transcribe(
    file_path: str,
    language,
    model: str,
    translate: bool = False,
    on_progress: Optional[ProgressCallback] = None,
) -> list[WhisperResult]:

    model = model or fw_default_model
    if model not in fw_models:
        raise NotSupportedModelException(NOT_SUPPORTED_MODEL_MESSAGE)

    task = "translate" if translate else "transcribe"
    # Make the bundled cuBLAS/cuDNN wheels loadable before CTranslate2 reaches
    # for them, so no CUDA Toolkit install is required.
    add_cuda_dll_dirs()
    model = WhisperModel(model, device="cuda", compute_type="float16")

    segments, info = model.transcribe(
        file_path,
        beam_size=5,
        language=language,
        temperature=0.8,  # Default is 0.6
        condition_on_previous_text=False,
        task=task,
        ## Keep this for future use
        # vad_filter=True,
        # vad_parameters=dict(
        #     speech_pad_ms=250,  # Wide cushion so no words get clipped at the ends
        #     threshold=0.40,  # Catches quiet/faint speech easily
        #     min_speech_duration_ms = 250,
        #     min_silence_duration_ms=400
        # )
    )

    print(
        "Detected language '%s' with probability %f"
        % (info.language, info.language_probability)
    )

    texts: list[WhisperResult] = []

    start_time = time.perf_counter()
    # segments is a generator: it decodes lazily, so the loop doubles as progress.
    for segment in segments:
        texts.append(
            {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
        )
        print(
            "[%s -> %s] %s"
            % (to_hh_mm_ss_ms(segment.start), to_hh_mm_ss_ms(segment.end), segment.text)
        )
        if on_progress and info.duration > 0:
            on_progress(min(segment.end / info.duration, 1.0))

    if on_progress:
        on_progress(1.0)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("Transcribe complete in %s" % (to_hh_mm_ss_ms(elapsed_time)))
    return texts
