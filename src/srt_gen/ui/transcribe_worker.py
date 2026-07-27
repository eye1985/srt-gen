import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from srt_gen.utils import is_apple
from srt_gen.models import mlx_models
from srt_gen.whisper import whisper_transcribe, NotSupportedModelException
from srt_gen.writer import write_to


class TranscribeWorker(QObject):
    progress = Signal(int)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.__last_percent = -1

    def emit_progress(self, fraction: float):
        """Turn a 0.0-1.0 decode fraction into a percentage signal.

        Called from the worker thread by the backend, once per decoded window; the
        emit itself is queued over to the GUI thread by Qt. Repeats are dropped so a
        long file doesn't flood the event loop with redundant repaints.
        """
        percent = int(fraction * 100)
        if percent != self.__last_percent:
            self.__last_percent = percent
            self.progress.emit(percent)

    def run_task(self, input_path: str, language: str, model: str, translate: bool):
        self.emit_progress(0.0)

        # Written next to the input, same name with an .srt suffix. The dialog hands
        # us an absolute path, so this has to stay absolute too.
        output_path = Path(input_path).with_suffix(".srt")

        if is_apple():
            try:
                texts = whisper_transcribe(
                    file_path=input_path,
                    language=language,
                    model=model,
                    translate=translate,
                    on_progress=self.emit_progress,
                )
                write_to(output_path, texts, srt=True)
                self.emit_progress(1.0)
            except NotSupportedModelException as e:
                print(f"{e}\n", file=sys.stderr)
                print("\n".join(mlx_models), file=sys.stderr)
        else:
            print("Not yet implemented", file=sys.stderr)
            pass

        self.finished.emit()  # finish
