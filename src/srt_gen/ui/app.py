from PySide6.QtCore import QSize, Qt, QThread
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QMainWindow,
    QPlainTextEdit,
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

        self.setWindowTitle("SRT Generator")
        self.path = ""

        # UI components
        self.button = QPushButton("Select file")
        self.button.clicked.connect(self.open_file_dialog)
        self.text_label = QLabel(self.path)
        # Hidden until there's a path to show. An empty but visible label is still
        # laid out, and being the only stretchable widget on screen it would take
        # the whole window height as blank space under the button.
        self.text_label.setVisible(False)
        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(self.run_transcribe)
        self.run_button.setVisible(False)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Log panel. The backend reports what it's doing by printing, so the worker
        # captures that and sends it here a line at a time.
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        # Segment lines add up on a long file, and only the recent ones are of any
        # use, so old ones are dropped rather than kept in memory forever.
        self.log_view.setMaximumBlockCount(5000)

        self.clear_log_button = QPushButton("Clear")
        self.clear_log_button.clicked.connect(self.log_view.clear)
        self.clear_log_button.setVisible(False)

        log_layout = QVBoxLayout()
        log_layout.addWidget(self.log_view)

        self.log_box = QGroupBox("Log")
        self.log_box.setLayout(log_layout)
        self.log_box.setVisible(False)

        # Layout
        self.settings = QWidget()
        self.options = TranscribeOptions()
        self.settings.setLayout(self.options.form_layout)
        self.settings.setVisible(False)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.run_button)
        buttons_layout.addWidget(self.clear_log_button)

        layout = QVBoxLayout()

        layout.addWidget(self.button)
        layout.addWidget(self.text_label)
        layout.addWidget(self.settings)
        layout.addWidget(self.progress_bar)
        # The only stretching widget, so it takes whatever the fixed-size window
        # has left over.
        layout.addWidget(self.log_box, stretch=1)
        layout.addLayout(buttons_layout)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "All files (*.*)"
        )

        if file_path:
            self.path = file_path
            self.text_label.setText(self.path)
            self.text_label.setVisible(True)
            self.settings.setVisible(True)
            self.run_button.setVisible(True)
            self.progress_bar.setVisible(True)
            self.log_box.setVisible(True)
            self.clear_log_button.setVisible(True)
        else:
            print("Cancelled")

    def append_log(self, message: str):
        """Add one line to the log panel, following the tail only when already there.

        Queued over from the worker thread by Qt, so this runs on the GUI thread.
        Sticking to the bottom unconditionally would yank the view away from anyone
        scrolling back through earlier output mid-run.
        """
        scroll_bar = self.log_view.verticalScrollBar()
        at_bottom = scroll_bar.value() >= scroll_bar.maximum() - 4

        self.log_view.appendPlainText(message)

        if at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())

    def run_transcribe(self):
        self.run_button.setEnabled(False)
        self.button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_view.clear()

        self.thread = QThread()
        # MLX walks its computation graph with a recursive DFS, which needs far more
        # stack than the 544K a QThread gets by default: without this the decode dies
        # with SIGBUS on the thread's guard page before the first segment is out. The
        # CLI path never hits it because the main thread already has 8MB. This only
        # reserves address space, so the unused part costs nothing.
        self.thread.setStackSize(32 * 1024 * 1024)
        self.worker = TranscribeWorker(
            input_path=self.path,
            auto_detect_lang=self.options.auto_detect_lang,
            language=self.options.language_code,
            model=self.options.model,
            translate=self.options.translate,
            temperature=self.options.temperature,
            condition_on_previous_text=self.options.condition_on_previous_text,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run_task)

        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log.connect(self.append_log)
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
