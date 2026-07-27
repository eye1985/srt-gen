from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
)

import sys
from srt_gen.ui.transcribe_options import TranscribeOptions


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRT Gen")
        self.path = ""

        # UI components
        self.button = QPushButton("Select file")
        self.button.clicked.connect(self.open_file_dialog)
        self.text_label = QLabel(self.path)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_transcribe)
        self.run_button.setVisible(False)

        # Layout
        self.settings = QWidget()
        self.options = TranscribeOptions()
        self.settings.setLayout(self.options.form_layout)
        self.settings.setVisible(False)

        layout = QVBoxLayout()

        layout.addWidget(self.button)
        layout.addWidget(self.text_label)
        layout.addWidget(self.settings)
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
        else:
            print("Cancelled")

    def run_transcribe(self):

        print(self.options.beam_size)
        print(self.options.language_code)
        print(self.options.condition_on_previous_text)
        print(self.options.temperature)
        print(self.options.translate)

        print("Transcribing ...")


def start_ui():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
