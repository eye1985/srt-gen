from writer import write_to
from utils import *
from whisper import whisper_transcribe
import argparse

parser = argparse.ArgumentParser("Add your input/output paths")
parser.add_argument("--input", type=str, help="eg. ./videos/video01.mp4")
parser.add_argument("--output", type=str, help="eg. ./results")
parser.add_argument("--language", type=str, help="eg. english")

args = parser.parse_args()

if args.input is None or args.output is None:
    print("You need to add your input/output paths. Use --help for assistance.")

print(args)

if is_apple():
    if not is_ffmpeg_available():
        print("ffmpeg not found in PATH")
    print("ffmpeg found, continues...")

    language = args.language if args.language is not None else "english"
    print("Language args was not provided, using default english")

    texts = whisper_transcribe(args.input, language)
    write_to(args.output, texts, srt=True)
    print("Done!")
else:
    print("Not yet implemented")
