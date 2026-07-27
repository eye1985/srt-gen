from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QFormLayout,
    QComboBox,
)

import sys
from srt_gen.languages import SUPPORTED_LANGUAGES


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRT Gen")
        self.path = ""
        self.beam_size = 5
        self.language_code = "en"
        self.temperature = 0.8
        self.condition_on_previous_text = False
        self.translate = False

        # UI components
        self.button = QPushButton("Select file")
        self.button.clicked.connect(self.open_file_dialog)
        self.text_label = QLabel(self.path)

        # Settings
        self.beam_size_box = QSpinBox(self)
        self.beam_size_box.setRange(1, 10)
        self.beam_size_box.setValue(self.beam_size)
        self.beam_size_box.valueChanged.connect(self.select_beam_size)

        self.language_combo_box = QComboBox(self)

        sorted_langs: list[str] = sorted(SUPPORTED_LANGUAGES)
        self.language_combo_box.addItems(sorted_langs)
        self.language_combo_box.setCurrentIndex(
            self.language_combo_box.findText(self.language_code)
        )
        self.language_combo_box.currentTextChanged.connect(self.select_language)

        self.temp_box = QDoubleSpinBox(self)
        self.temp_box.setRange(0.0, 1.0)
        self.temp_box.setSingleStep(0.1)
        self.temp_box.setDecimals(2)
        self.temp_box.setValue(self.temperature)
        self.temp_box.valueChanged.connect(self.select_temperature)

        self.condition_box = QCheckBox(self)
        self.condition_box.setChecked(self.condition_on_previous_text)
        self.condition_box.toggled.connect(self.select_condition_on_previous_text)

        self.translate_box = QCheckBox(self)
        self.translate_box.setChecked(self.translate)
        self.translate_box.toggled.connect(self.select_translate)

        # Layout
        self.settings = QWidget()
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form_layout.addRow("Beam Size:", self.beam_size_box)
        form_layout.addRow("Language:", self.language_combo_box)
        form_layout.addRow("Temperature:", self.temp_box)
        form_layout.addRow("Condition on previous text:", self.condition_box)
        form_layout.addRow("Translate to English:", self.translate_box)
        self.settings.setLayout(form_layout)
        self.settings.setVisible(False)

        layout = QVBoxLayout()

        layout.addWidget(self.button)
        layout.addWidget(self.text_label)
        layout.addWidget(self.settings)

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
        else:
            print("Cancelled")

    def select_beam_size(self, value):
        self.beam_size = value

    def select_language(self, text):
        self.language_code = text

    def select_temperature(self, value):
        self.temperature = value

    def select_condition_on_previous_text(self, checked):
        self.condition_on_previous_text = checked

    def select_translate(self, checked):
        self.translate = checked


def start_ui():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
