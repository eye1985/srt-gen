from PySide6.QtWidgets import (
    QSpinBox,
    QComboBox,
    QDoubleSpinBox,
    QCheckBox,
    QFormLayout,
)
from PySide6.QtCore import Qt


from srt_gen.languages import SUPPORTED_LANGUAGES
from srt_gen.models import default_model_for_platform, models_for_platform
from srt_gen.utils import is_apple


class TranscribeOptions:
    def __init__(self):
        self.__beam_size = 5
        self.__auto_detect_lang = True
        self.__language_code = "en"
        self.__temperature = 0.8
        self.__condition_on_previous_text = False
        self.__translate = False
        self.__model = default_model_for_platform()

        # Only the models the platform's backend can actually load are offered,
        # so the selection can never trip NotSupportedModelException.
        self.model_combo_box = QComboBox()
        self.model_combo_box.addItems(models_for_platform())
        self.model_combo_box.setCurrentIndex(
            self.model_combo_box.findText(self.__model)
        )
        self.model_combo_box.currentTextChanged.connect(self.select_model)

        self.beam_size_box = QSpinBox()
        self.beam_size_box.setRange(1, 10)
        self.beam_size_box.setValue(self.__beam_size)
        self.beam_size_box.valueChanged.connect(self.select_beam_size)

        self.auto_detect_lang_checkbox = QCheckBox()
        self.auto_detect_lang_checkbox.setChecked(self.__auto_detect_lang)
        self.auto_detect_lang_checkbox.toggled.connect(self.set_auto_detect_lang)

        self.language_combo_box = QComboBox()
        self.language_combo_box.setDisabled(True)

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
        self.__form_layout.setContentsMargins(0, 0, 0, 0)
        self.__form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.__form_layout.addRow("Model:", self.model_combo_box)
        # mlx has no beam search, so the option is meaningless on Apple Silicon.
        if not is_apple():
            self.__form_layout.addRow("Beam Size:", self.beam_size_box)
        self.__form_layout.addRow(
            "Auto detect language:", self.auto_detect_lang_checkbox
        )
        self.__form_layout.addRow("Language:", self.language_combo_box)
        self.__form_layout.addRow("Temperature:", self.temp_box)
        self.__form_layout.addRow("Condition on previous text:", self.condition_box)
        self.__form_layout.addRow("Translate to English:", self.translate_box)

    def select_model(self, text):
        self.__model = text

    def select_beam_size(self, value):
        self.__beam_size = value

    def set_auto_detect_lang(self, checked):
        self.__auto_detect_lang = checked
        self.language_combo_box.setEnabled(not checked)

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
    def model(self):
        return self.__model

    @property
    def beam_size(self):
        return self.__beam_size

    @property
    def auto_detect_lang(self):
        return self.__auto_detect_lang

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
