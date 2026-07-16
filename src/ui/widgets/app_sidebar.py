"""High-frequency, per-translation controls for the main workspace."""

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.translation import RuntimeOverrides
from src.stores.settings_store import get_settings_store
from src.utils.file_utils import select_files


LANGUAGE_ITEMS = [
    ("English", "en"),
    ("简体中文", "zh"),
    ("日本語", "ja"),
    ("한국어", "ko"),
    ("Français", "fr"),
    ("Deutsch", "de"),
    ("Español", "es"),
    ("Português", "pt"),
    ("Русский", "ru"),
    ("العربية", "ar"),
    ("Italiano", "it"),
]


class AppSidebar(QWidget):
    """Collect task-level overrides without mutating persisted defaults."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_store = get_settings_store()
        self.setup_ui()
        self.load_settings()
        self._connect_signals()

    def setup_ui(self) -> None:
        self.setObjectName("quick_settings")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(14)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        self.lang_in_combo = self._language_combo()
        self.lang_out_combo = self._language_combo()
        grid.addWidget(self._field("源语言", self.lang_in_combo), 0, 0)
        grid.addWidget(self._field("目标语言", self.lang_out_combo), 0, 1)

        self.model_combo = QComboBox()
        self.model_combo.addItem("请先在设置中配置模型")
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        grid.addWidget(self._field("翻译模型", self.model_combo), 1, 0, 1, 2)

        self.pages_input = QLineEdit()
        self.pages_input.setPlaceholderText("全部页面，例如 1-5, 8")
        self.output_mode_combo = QComboBox()
        self.output_mode_combo.addItem("双语 + 单语", "both")
        self.output_mode_combo.addItem("仅双语 PDF", "dual")
        self.output_mode_combo.addItem("仅单语 PDF", "mono")
        self.output_mode_combo.currentIndexChanged.connect(
            self._sync_bilingual_controls
        )
        grid.addWidget(
            self._field("页面范围", self.pages_input, "留空翻译全部页面"), 2, 0
        )
        grid.addWidget(self._field("输出模式", self.output_mode_combo), 2, 1)

        self.bilingual_layout_combo = QComboBox()
        self.bilingual_layout_combo.addItem("标准双语", "standard")
        self.bilingual_layout_combo.addItem("页面交替 · 原文在前", "source_first")
        self.bilingual_layout_combo.addItem("页面交替 · 译文在前", "translated_first")
        grid.addWidget(self._field("双语排版", self.bilingual_layout_combo), 3, 0, 1, 2)
        layout.addLayout(grid)

        divider = QFrame()
        divider.setObjectName("section_divider")
        divider.setFrameShape(QFrame.HLine)
        layout.addWidget(divider)

        terminology_header = QHBoxLayout()
        terminology_header.setSpacing(8)
        terminology_title = QLabel("术语增强")
        terminology_title.setObjectName("compact_section_title")
        terminology_header.addWidget(terminology_title)
        terminology_header.addStretch()
        self.auto_glossary_check = QCheckBox("自动提取术语")
        self.auto_glossary_check.setObjectName("feature_toggle")
        terminology_header.addWidget(self.auto_glossary_check)
        layout.addLayout(terminology_header)

        glossary_row = QHBoxLayout()
        glossary_row.setSpacing(8)
        self.glossary_input = QLineEdit()
        self.glossary_input.setPlaceholderText("可选：添加一个或多个 CSV 术语表")
        glossary_row.addWidget(self.glossary_input, 1)
        self.glossary_button = QPushButton("选择文件")
        self.glossary_button.setObjectName("secondary_button")
        self.glossary_button.clicked.connect(self._choose_glossaries)
        glossary_row.addWidget(self.glossary_button)
        layout.addLayout(glossary_row)

    def _connect_signals(self) -> None:
        self.settings_store.providers_changed.connect(self._load_models)
        self.settings_store.translation_settings_changed.connect(
            lambda _changes: self.load_settings()
        )
        self.settings_store.pdf_settings_changed.connect(
            lambda _changes: self.load_settings()
        )
        self.settings_store.path_settings_changed.connect(
            lambda _changes: self.load_settings()
        )

    @staticmethod
    def _language_combo() -> QComboBox:
        combo = QComboBox()
        for label, code in LANGUAGE_ITEMS:
            combo.addItem(f"{label}  ({code})", code)
        return combo

    @staticmethod
    def _field(label_text: str, control: QWidget, hint: str = "") -> QFrame:
        field = QFrame()
        field.setObjectName("field_block")
        layout = QVBoxLayout(field)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        label = QLabel(label_text)
        label.setObjectName("field_label")
        layout.addWidget(label)
        layout.addWidget(control)
        if hint:
            hint_label = QLabel(hint)
            hint_label.setObjectName("field_hint")
            layout.addWidget(hint_label)
        layout.addStretch()
        return field

    def load_settings(self) -> None:
        settings = self.settings_store.get_settings()
        trans = settings.translation
        pdf = settings.pdf

        self._set_combo_data(self.lang_in_combo, trans.lang_in)
        self._set_combo_data(self.lang_out_combo, trans.lang_out)
        self.auto_glossary_check.setChecked(trans.auto_extract_glossary)
        self.glossary_input.setText(settings.paths.glossary_files or "")

        if pdf.output_dual and pdf.output_mono:
            output_mode = "both"
        elif pdf.output_dual:
            output_mode = "dual"
        else:
            output_mode = "mono"
        self._set_combo_data(self.output_mode_combo, output_mode)

        if not pdf.use_alternating_pages_dual:
            layout_mode = "standard"
        elif pdf.dual_translate_first:
            layout_mode = "translated_first"
        else:
            layout_mode = "source_first"
        self._set_combo_data(self.bilingual_layout_combo, layout_mode)
        self._load_models()
        self._sync_bilingual_controls()

    @staticmethod
    def _set_combo_data(combo: QComboBox, value) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _load_models(self, _providers=None) -> None:
        selected_model = self.settings_store.get_selected_model()
        selected_model_id = selected_model.id if selected_model else None
        models = [
            (model.id, f"{provider.name} · {model.display_name}")
            for provider in self.settings_store.get_providers()
            for model in provider.models
        ]

        with QSignalBlocker(self.model_combo):
            self.model_combo.clear()
            if not models:
                self.model_combo.addItem("请先在设置中配置模型")
                self.model_combo.setEnabled(False)
            else:
                self.model_combo.setEnabled(True)
                for model_id, display_name in models:
                    self.model_combo.addItem(display_name, model_id)
                index = self.model_combo.findData(selected_model_id)
                self.model_combo.setCurrentIndex(index if index >= 0 else 0)

        current_model_id = self.model_combo.currentData()
        if current_model_id and current_model_id != selected_model_id:
            self.settings_store.select_model(current_model_id)

    def _on_model_changed(self, index: int) -> None:
        model_id = self.model_combo.itemData(index)
        if model_id:
            self.settings_store.select_model(model_id)

    def _sync_bilingual_controls(self, _index: int = -1) -> None:
        self.bilingual_layout_combo.setEnabled(
            self.output_mode_combo.currentData() != "mono"
        )

    def _choose_glossaries(self) -> None:
        files = select_files(self, "CSV Files (*.csv)", multiple=True)
        if files:
            self.glossary_input.setText(",".join(files))

    def get_config(self) -> RuntimeOverrides:
        settings = self.settings_store.get_settings()
        output_mode = self.output_mode_combo.currentData()
        layout_mode = self.bilingual_layout_combo.currentData()
        glossary_files = self.glossary_input.text().strip()

        return RuntimeOverrides(
            lang_in=self.lang_in_combo.currentData() or settings.translation.lang_in,
            lang_out=self.lang_out_combo.currentData() or settings.translation.lang_out,
            pages=self.pages_input.text().strip() or None,
            qps=settings.translation.qps,
            output_dual=output_mode in ("both", "dual"),
            output_mono=output_mode in ("both", "mono"),
            use_alternating_pages_dual=layout_mode != "standard",
            dual_translate_first=layout_mode == "translated_first",
            auto_extract_glossary=self.auto_glossary_check.isChecked(),
            glossary_files=glossary_files or None,
        )
