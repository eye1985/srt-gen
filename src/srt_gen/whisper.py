import time
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from typing import TypedDict
from .utils import add_cuda_dll_dirs, to_hh_mm_ss_ms

WhisperResult = TypedDict(
    "WhisperResult",
    {
        "start": float,
        "end": float,
        "text": str,
    },
)

mlx_default_model = "mlx-community/whisper-large-v3-mlx"

# Canonical fp16 MLX conversions hosted by the mlx-community org, one per
# official Whisper size. Values are the HF repo ids passed as `path_or_hf_repo`.
# (Quantized -4bit/-8bit/-fp32 variants and language-specific fine-tunes are
# omitted; add them here if needed.)
mlx_models = frozenset(
    [
        "mlx-community/whisper-tiny-mlx",
        "mlx-community/whisper-tiny.en-mlx",
        "mlx-community/whisper-base-mlx",
        "mlx-community/whisper-base.en-mlx",
        "mlx-community/whisper-small-mlx",
        "mlx-community/whisper-small.en-mlx",
        "mlx-community/whisper-medium-mlx",
        "mlx-community/whisper-medium.en-mlx",
        "mlx-community/whisper-large-mlx",
        "mlx-community/whisper-large-v1-mlx",
        "mlx-community/whisper-large-v2-mlx",
        mlx_default_model,
        "mlx-community/whisper-large-v3-turbo",
        "mlx-community/distil-whisper-large-v3",
        "mlx-community/distil-whisper-medium.en",
    ]
)

fw_default_model = "large-v3"
# Model names accepted by faster-whisper (faster_whisper.utils._MODELS). These
# are downloaded from the Systran HF repos on first use.
fw_models = frozenset(
    [
        "tiny",
        "tiny.en",
        "base",
        "base.en",
        "small",
        "small.en",
        "medium",
        "medium.en",
        "large",
        "large-v1",
        "large-v2",
        fw_default_model,
        "large-v3-turbo",
        "turbo",
        "distil-small.en",
        "distil-medium.en",
        "distil-large-v2",
        "distil-large-v3",
        "distil-large-v3.5",
    ]
)


class NotSupportedModelException(Exception):
    pass


NOT_SUPPORTED_MODEL_MESSAGE = "Please pick a model from the supported list."


def whisper_transcribe(
    file_path: str,
    language,
    model: str,
    translate: bool = False,
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
    file_path: str, language, model: str, translate: bool = False
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
    for segment in segments:
        texts.append(
            {"start": segment.start, "end": segment.end, "text": segment.text.strip()}
        )
        print(
            "[%s -> %s] %s"
            % (to_hh_mm_ss_ms(segment.start), to_hh_mm_ss_ms(segment.end), segment.text)
        )

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print("Transcribe complete in %s" % (to_hh_mm_ss_ms(elapsed_time)))
    return texts
