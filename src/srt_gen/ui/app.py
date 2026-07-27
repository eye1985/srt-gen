from PySide6.QtCore import QSize, Qt, QThread
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QMessageBox,
    QProgressBar,
)

import sys
from srt_gen.ui.transcribe_options import TranscribeOptions
from srt_gen.ui.transcribe_worker import TranscribeWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.worker = None

        self.setWindowTitle("SRT Gen")
        self.path = ""

        # UI components
        self.button = QPushButton("Select file")
        self.button.clicked.connect(self.open_file_dialog)
        self.text_label = QLabel(self.path)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_transcribe)
        self.run_button.setVisible(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Layout
        self.settings = QWidget()
        self.options = TranscribeOptions()
        self.settings.setLayout(self.options.form_layout)
        self.settings.setVisible(False)

        layout = QVBoxLayout()

        layout.addWidget(self.button)
        layout.addWidget(self.text_label)
        layout.addWidget(self.settings)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.run_button)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
        self.setFixedSize(QSize(800, 600))

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All files (*.*)"
        )

        if file_path:
            self.path = file_path
            self.text_label.setText(self.path)
            self.settings.setVisible(True)
            self.run_button.setVisible(True)
            self.progress_bar.setVisible(True)
        else:
            print("Cancelled")

    def run_transcribe(self):
        self.run_button.setEnabled(False)
        self.button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.thread = QThread()
        self.worker = TranscribeWorker(
            input_path=self.path,
            auto_detect_lang=self.options.auto_detect_lang,
            language=self.options.language_code,
            model=self.options.model,
            translate=self.options.translate,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_task)

        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.failed.connect(self.on_transcribe_failed)
        self.worker.finished.connect(self.on_transcribe_finished)
        self.worker.finished.connect(self.thread.quit)

        self.thread.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_transcribe_failed(self, message: str):
        QMessageBox.critical(self, "Transcribe failed", message)

    def on_transcribe_finished(self):
        self.run_button.setEnabled(True)
        self.button.setEnabled(True)


def start_ui():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
