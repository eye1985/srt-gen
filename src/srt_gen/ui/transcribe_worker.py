from pathlib import Path

from PySide6.QtCore import QObject, Signal

from srt_gen.utils import is_apple
from srt_gen.models import mlx_models
from srt_gen.whisper import whisper_transcribe, NotSupportedModelException
from srt_gen.writer import write_to


class TranscribeWorker(QObject):
    progress = Signal(int)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, input_path: str, language: str, model: str, translate: bool):
        super().__init__()
        self.__last_percent = -1
        self.__input_path = input_path
        self.__language = language
        self.__model = model
        self.__translate = translate

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

    def run_task(self):
        """Entry point for the worker thread.

        Connected straight to QThread.started as a bound slot: the worker lives in
        that thread, so Qt queues the call onto it. Wrapping this in a lambda instead
        would pin it to the GUI thread and freeze the window for the whole decode.
        """
        self.emit_progress(0.0)

        # Written next to the input, same name with an .srt suffix. The dialog hands
        # us an absolute path, so this has to stay absolute too.
        output_path = Path(self.__input_path).with_suffix(".srt")

        try:
            if not is_apple():
                raise NotImplementedError(
                    "Only Apple Silicon is supported from the UI for now."
                )

            texts = whisper_transcribe(
                file_path=self.__input_path,
                language=self.__language,
                model=self.__model,
                translate=self.__translate,
                on_progress=self.emit_progress,
            )
            write_to(output_path, texts, srt=True)
            self.emit_progress(1.0)
        except NotSupportedModelException as e:
            self.failed.emit("%s\n\n%s" % (e, "\n".join(mlx_models)))
        except Exception as e:
            # Anything escaping here would otherwise die silently in the worker
            # thread, leaving the UI stuck on a half-filled progress bar.
            self.failed.emit(str(e))
        finally:
            # Always emitted, so the thread quits even after a failure.
            self.finished.emit()
