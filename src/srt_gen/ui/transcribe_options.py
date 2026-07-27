from PySide6.QtWidgets import (
    QSpinBox,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QFormLayout,
)
from PySide6.QtCore import Qt


from srt_gen.languages import SUPPORTED_LANGUAGES


class TranscribeOptions:
    def __init__(self):
        self.__beam_size = 5
        self.__language_code = "en"
        self.__temperature = 0.8
        self.__condition_on_previous_text = False
        self.__translate = False

        self.beam_size_box = QSpinBox()
        self.beam_size_box.setRange(1, 10)
        self.beam_size_box.setValue(self.__beam_size)
        self.beam_size_box.valueChanged.connect(self.select_beam_size)

        self.language_combo_box = QComboBox()

        sorted_langs: list[str] = sorted(SUPPORTED_LANGUAGES)
        self.language_combo_box.addItems(sorted_langs)
        self.language_combo_box.setCurrentIndex(
            self.language_combo_box.findText(self.__language_code)
        )
        self.language_combo_box.currentTextChanged.connect(self.select_language)

        self.temp_box = QDoubleSpinBox()
        self.temp_box.setRange(0.0, 1.0)
        self.temp_box.setSingleStep(0.1)
        self.temp_box.setDecimals(2)
        self.temp_box.setValue(self.__temperature)
        self.temp_box.valueChanged.connect(self.select_temperature)

        self.condition_box = QCheckBox()
        self.condition_box.setChecked(self.__condition_on_previous_text)
        self.condition_box.toggled.connect(self.select_condition_on_previous_text)

        self.translate_box = QCheckBox()
        self.translate_box.setChecked(self.__translate)
        self.translate_box.toggled.connect(self.select_translate)

        self.__form_layout = QFormLayout()
        self.__form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.__form_layout.addRow("Beam Size:", self.beam_size_box)
        self.__form_layout.addRow("Language:", self.language_combo_box)
        self.__form_layout.addRow("Temperature:", self.temp_box)
        self.__form_layout.addRow("Condition on previous text:", self.condition_box)
        self.__form_layout.addRow("Translate to English:", self.translate_box)

    def select_beam_size(self, value):
        self.__beam_size = value

    def select_language(self, text):
        self.__language_code = text

    def select_temperature(self, value):
        self.__temperature = value

    def select_condition_on_previous_text(self, checked):
        self.__condition_on_previous_text = checked

    def select_translate(self, checked):
        self.__translate = checked

    @property
    def form_layout(self):
        return self.__form_layout

    @property
    def beam_size(self):
        return self.__beam_size

    @property
    def language_code(self):
        return self.__language_code

    @property
    def temperature(self):
        return self.__temperature

    @property
    def condition_on_previous_text(self):
        return self.__condition_on_previous_text

    @property
    def translate(self):
        return self.__translate
