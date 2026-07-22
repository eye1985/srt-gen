from whisper import WhisperResult
from utils import to_hh_mm_ss_ms


def write_to(path, data: list[WhisperResult], new_line: bool = True, overwrite: bool = True, srt: bool = False):
    with open(path, "w" if overwrite else "a") as f:
        if srt:
            for i, d in enumerate(data):
                print("Writing to " + path)

                start = to_hh_mm_ss_ms(d["start"])
                end = to_hh_mm_ss_ms(d["end"])
                index = i + 1

                f.write(f"{index}\n")
                f.write(f"{start} --> {end}\n")
                f.write(f"{d["text"]}\n\n")
        else:
            for d in data:
                print("Writing to " + path)
                f.write(f"{d["text"]}\n" if new_line else d["text"])

        print("Writing done!")
