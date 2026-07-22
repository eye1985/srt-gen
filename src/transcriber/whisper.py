import mlx_whisper
from typing import TypedDict

model = "mlx-community/whisper-large-v3-mlx"
WhisperResult = TypedDict("WhisperResult", {
    "start": float,
    "end": float,
    "text": str,
})


def whisper_transcribe(audio_file: str, language="english") -> list[WhisperResult]:
    output = mlx_whisper.transcribe(audio_file, path_or_hf_repo=model,
                                    word_timestamps=True, language=language)
    segments = output["segments"]
    texts = list(
        map(lambda x: {"start": x["start"], "end": x["end"], "text": x["text"].strip()}, segments))

    print("Transcribe complete")
    return texts
