from functools import cache

import numpy as np
import soundfile as sf
from mlx_audio.tts.utils import load_model

MODEL = "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit"
voice = "Vivian"


@cache
def get_model():
    return load_model(MODEL)


def generate_wav(texts: list[str], lang_code="english", output_path: str = "./bin/output.wav"):
    model = get_model()
    chunks = []
    sr = None

    temp_ref_audio = None
    for index, text in enumerate(texts):
        for result in model.generate(text, voice=voice, lang_code=lang_code, ref_audio=temp_ref_audio,
                                     ref_text=None if index == 0 else texts[0]):
            if index == 0:
                temp_ref_audio = result.audio

            chunks.append(result.audio)
            sr = result.sample_rate

            print("Chunk complete")
    if sr is not None:
        sf.write(output_path, np.concatenate(chunks), sr)
    else:
        print("no audio found")
