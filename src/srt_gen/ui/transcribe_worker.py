from pathlib import Path

from PySide6.QtCore import QObject, Signal

from srt_gen.ui.log_stream import capture_output
from srt_gen.utils import is_apple
from srt_gen.models import mlx_models
from srt_gen.whisper import whisper_transcribe, NotSupportedModelException
from srt_gen.writer import write_to


class TranscribeWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        input_path: str,
        auto_detect_lang: bool,
        language: str,
        model: str,
        translate: bool,
        temperature: float,
        condition_on_previous_text: bool,
    ):
        super().__init__()
        self.__last_percent = -1
        self.__input_path = input_path
        self.__language = language
        self.__model = model
        self.__translate = translate
        self.__auto_detect_lang = auto_detect_lang
        self.__temperature = temperature
        self.__condition_on_previous_text = condition_on_previous_text

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

        # Everything printed in here, by us or by the backend, ends up in the log
        # panel as well as on the terminal.
        with capture_output(self.log.emit):
            try:
                print("Starting transcribe: %s" % self.__input_path)
                print("Model: %s" % self.__model)
                if self.__translate:
                    print("Translating to English")

                if not is_apple():
                    raise NotImplementedError(
                        "Only Apple Silicon is supported from the UI for now."
                    )

                texts = whisper_transcribe(
                    file_path=self.__input_path,
                    # None lets whisper detect the language itself
                    language=None if self.__auto_detect_lang else self.__language,
                    model=self.__model,
                    translate=self.__translate,
                    temperature=self.__temperature,
                    condition_on_previous_text=self.__condition_on_previous_text,
                    on_progress=self.emit_progress,
                )
                write_to(output_path, texts, srt=True)
                print("Wrote %s" % output_path)
                self.emit_progress(1.0)
            except NotSupportedModelException as e:
                print("Failed: %s" % e)
                self.failed.emit("%s\n\n%s" % (e, "\n".join(mlx_models)))
            except Exception as e:
                # Anything escaping here would otherwise die silently in the worker
                # thread, leaving the UI stuck on a half-filled progress bar. The log
                # keeps a copy, since the dialog is gone as soon as it's dismissed.
                print("Failed: %s" % e)
                self.failed.emit(str(e))
            finally:
                # Always emitted, so the thread quits even after a failure.
                self.finished.emit()
