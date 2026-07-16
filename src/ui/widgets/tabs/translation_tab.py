"""Translation defaults, quality and terminology settings."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


LANGUAGE_LABELS = [
    ("中文 (zh)", "zh"),
    ("English (en)", "en"),
    ("日本語 (ja)", "ja"),
    ("한국어 (ko)", "ko"),
    ("Français (fr)", "fr"),
    ("Deutsch (de)", "de"),
    ("Español (es)", "es"),
    ("Português (pt)", "pt"),
    ("Русский (ru)", "ru"),
    ("العربية (ar)", "ar"),
    ("Italiano (it)", "it"),
]


class TranslationTab(QWidget):
    """Edit defaults that should not crowd every translation task."""

    def __init__(self, settings_store):
        super().__init__()
        self.settings_store = settings_store
        self.setup_ui()
        self.settings_store.providers_changed.connect(self._load_term_models)
        self.load_settings()

    def setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("settings_page_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("settings_page_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 14, 20)
        layout.setSpacing(18)

        layout.addWidget(self._group_title("任务默认值"))
        default_hint = QLabel("首页可按任务临时覆盖语言；这里保存下次启动时的默认值。")
        default_hint.setObjectName("settings_hint")
        default_hint.setWordWrap(True)
        layout.addWidget(default_hint)

        defaults_form = QFormLayout()
        defaults_form.setHorizontalSpacing(20)
        defaults_form.setVerticalSpacing(12)
        self.lang_in_combo = self._language_combo()
        defaults_form.addRow("默认源语言", self.lang_in_combo)
        self.lang_out_combo = self._language_combo()
        defaults_form.addRow("默认目标语言", self.lang_out_combo)

        self.qps_spin = QSpinBox()
        self.qps_spin.setRange(1, 100)
        self.qps_spin.setSuffix(" 次 / 秒")
        defaults_form.addRow("请求速率 QPS", self.qps_spin)

        self.min_text_length_spin = QSpinBox()
        self.min_text_length_spin.setRange(0, 100)
        self.min_text_length_spin.setSuffix(" 字符")
        defaults_form.addRow("最小翻译文本", self.min_text_length_spin)
        layout.addLayout(defaults_form)

        layout.addWidget(self._group_title("术语提取"))
        self.auto_extract_glossary = QCheckBox("默认自动提取术语")
        layout.addWidget(self.auto_extract_glossary)
        self.save_auto_extracted_glossary = QCheckBox("保存自动提取的术语表")
        layout.addWidget(self.save_auto_extracted_glossary)
        self.use_separate_term_model = QCheckBox("使用独立模型提取术语")
        layout.addWidget(self.use_separate_term_model)

        self.term_settings_frame = QFrame()
        self.term_settings_frame.setObjectName("inset_panel")
        term_form = QFormLayout(self.term_settings_frame)
        term_form.setContentsMargins(16, 14, 16, 14)
        term_form.setHorizontalSpacing(18)
        term_form.setVerticalSpacing(10)

        self.term_model_combo = QComboBox()
        self.term_model_combo.currentIndexChanged.connect(self._sync_term_controls)
        term_form.addRow("术语模型", self.term_model_combo)

        self.term_reasoning_combo = QComboBox()
        self.term_reasoning_combo.addItem("跟随模型默认", "")
        self.term_reasoning_combo.addItem("低", "low")
        self.term_reasoning_combo.addItem("中", "medium")
        self.term_reasoning_combo.addItem("高", "high")
        term_form.addRow("推理强度", self.term_reasoning_combo)

        self.custom_term_frame = QFrame()
        custom_form = QFormLayout(self.custom_term_frame)
        custom_form.setContentsMargins(0, 4, 0, 0)
        custom_form.setHorizontalSpacing(18)
        custom_form.setVerticalSpacing(10)
        self.custom_term_model = QLineEdit()
        self.custom_term_model.setPlaceholderText("例如 gpt-4.1-mini")
        custom_form.addRow("自定义模型", self.custom_term_model)
        self.custom_term_base_url = QLineEdit()
        self.custom_term_base_url.setPlaceholderText("https://.../v1")
        custom_form.addRow("Base URL", self.custom_term_base_url)
        self.custom_term_api_key = QLineEdit()
        self.custom_term_api_key.setEchoMode(QLineEdit.Password)
        self.custom_term_api_key.setPlaceholderText("API Key")
        custom_form.addRow("API Key", self.custom_term_api_key)
        term_form.addRow(self.custom_term_frame)
        layout.addWidget(self.term_settings_frame)

        self.use_separate_term_model.toggled.connect(self._sync_term_controls)

        layout.addWidget(self._group_title("翻译策略"))
        self.add_formula_placehold_hint = QCheckBox("向模型添加公式占位符提示")
        layout.addWidget(self.add_formula_placehold_hint)
        self.ignore_cache = QCheckBox("忽略已有翻译缓存")
        layout.addWidget(self.ignore_cache)

        prompt_label = QLabel("自定义系统提示词")
        prompt_label.setObjectName("field_label")
        layout.addWidget(prompt_label)
        self.custom_system_prompt = QTextEdit()
        self.custom_system_prompt.setMinimumHeight(112)
        self.custom_system_prompt.setPlaceholderText(
            "可选：补充领域、语气或专有名词要求。请勿重复基础翻译指令。"
        )
        layout.addWidget(self.custom_system_prompt)
        layout.addStretch()

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    @staticmethod
    def _group_title(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("settings_group_title")
        return label

    @staticmethod
    def _language_combo() -> QComboBox:
        combo = QComboBox()
        for label, code in LANGUAGE_LABELS:
            combo.addItem(label, code)
        return combo

    @staticmethod
    def _set_combo_data(combo: QComboBox, value) -> None:
        index = combo.findData(value)
        combo.setCurrentIndex(index if index >= 0 else 0)

    def _load_term_models(self, _providers=None) -> None:
        selected = self.term_model_combo.currentData()
        self.term_model_combo.clear()
        self.term_model_combo.addItem("自定义 OpenAI 兼容连接", "")
        if hasattr(self.settings_store, "get_all_models"):
            for item in self.settings_store.get_all_models():
                model = item["model"]
                provider = item["provider"]
                self.term_model_combo.addItem(
                    f"{provider.name} · {model.display_name}", model.id
                )
        self._set_combo_data(self.term_model_combo, selected)

    def _sync_term_controls(self, _value=None) -> None:
        enabled = self.use_separate_term_model.isChecked()
        self.term_settings_frame.setVisible(enabled)
        use_custom = enabled and not bool(self.term_model_combo.currentData())
        self.custom_term_frame.setVisible(use_custom)

    def load_settings(self) -> None:
        settings = self.settings_store.get_settings()
        trans = settings.translation
        term = settings.term_extraction

        self._set_combo_data(self.lang_in_combo, trans.lang_in)
        self._set_combo_data(self.lang_out_combo, trans.lang_out)
        self.qps_spin.setValue(trans.qps)
        self.min_text_length_spin.setValue(trans.min_text_length)
        self.auto_extract_glossary.setChecked(trans.auto_extract_glossary)
        self.add_formula_placehold_hint.setChecked(trans.add_formula_placehold_hint)
        self.ignore_cache.setChecked(trans.ignore_cache)
        self.save_auto_extracted_glossary.setChecked(trans.save_auto_extracted_glossary)
        self.custom_system_prompt.setPlainText(trans.custom_system_prompt)

        self._load_term_models()
        self.use_separate_term_model.setChecked(term.use_separate_config)
        self._set_combo_data(self.term_model_combo, term.model_config_id)
        self._set_combo_data(self.term_reasoning_combo, term.reasoning)
        self.custom_term_api_key.setText(term.custom_api_key)
        self.custom_term_base_url.setText(term.custom_base_url)
        self.custom_term_model.setText(term.custom_model)
        self._sync_term_controls()

    def save_settings(self) -> None:
        self.settings_store.update_translation_settings(
            lang_in=self.lang_in_combo.currentData() or "en",
            lang_out=self.lang_out_combo.currentData() or "zh",
            qps=self.qps_spin.value(),
            min_text_length=self.min_text_length_spin.value(),
            auto_extract_glossary=self.auto_extract_glossary.isChecked(),
            add_formula_placehold_hint=self.add_formula_placehold_hint.isChecked(),
            ignore_cache=self.ignore_cache.isChecked(),
            save_auto_extracted_glossary=self.save_auto_extracted_glossary.isChecked(),
            custom_system_prompt=self.custom_system_prompt.toPlainText(),
        )
        self.settings_store.update_term_extraction_settings(
            use_separate_config=self.use_separate_term_model.isChecked(),
            model_config_id=self.term_model_combo.currentData() or "",
            custom_api_key=self.custom_term_api_key.text().strip(),
            custom_base_url=self.custom_term_base_url.text().strip(),
            custom_model=self.custom_term_model.text().strip(),
            reasoning=self.term_reasoning_combo.currentData() or "",
        )
