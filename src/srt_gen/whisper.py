from faster_whisper import WhisperModel
from typing import TypedDict

WhisperResult = TypedDict("WhisperResult", {
    "start": float,
    "end": float,
    "text": str,
})


def whisper_transcribe(file_path: str, language="english") -> list[WhisperResult]:
    import mlx_whisper  # only importable/usable on Apple Silicon (Metal-based)
    model = "mlx-community/whisper-large-v3-mlx"

    output = mlx_whisper.transcribe(file_path, path_or_hf_repo=model,
                                    word_timestamps=True, language=language)
    segments = output["segments"]
    texts = list(
        map(lambda x: {"start": x["start"], "end": x["end"], "text": x["text"].strip()}, segments))

    print("Transcribe complete")
    return texts


def faster_whisper_transcribe(file_path: str, language="en"):
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    segments, info = model.transcribe(file_path, beam_size=5, language=language)

    print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

    texts: list[WhisperResult] = []
    for segment in segments:
        texts.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    return texts
