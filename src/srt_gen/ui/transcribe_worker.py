from PySide6.QtCore import QObject, Signal


class TranscribeWorker(QObject):
    progress = Signal(int)
    finished = Signal()

    def run_task(self):
        self.progress.emit(1)




        self.finished.emit() #finish