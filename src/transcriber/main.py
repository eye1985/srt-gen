import writer

from utils import *
from whisper import whisper_transcribe
from speech import generate_wav

if is_apple():
    if not is_ffmpeg_available():
        print("ffmpeg not found in PATH")

    print("ffmpeg found, continues...")

    texts = whisper_transcribe("./bin/youtube.mp4", "english")
    # generate_wav(texts, "mandarin")
    writer.write_to("bin/transcribe.txt", texts, srt=True)
    print("Done!")
else:
    print("Not yet implemented")
