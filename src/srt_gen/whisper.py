import time
from faster_whisper import WhisperModel
from faster_whisper.audio import decode_audio
from typing import TypedDict
from .utils import to_hh_mm_ss_ms

WhisperResult = TypedDict(
    "WhisperResult",
    {
        "start": float,
        "end": float,
        "text": str,
    },
)


def whisper_transcribe(
    file_path: str, language, translate: bool = False
) -> list[WhisperResult]:
    import mlx_whisper  # only importable/usable on Apple Silicon (Metal-based)

    model = "mlx-community/whisper-large-v3-mlx"

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
    file_path: str, language, translate: bool = False
) -> list[WhisperResult]:
    task = "translate" if translate else "transcribe"
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")

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
