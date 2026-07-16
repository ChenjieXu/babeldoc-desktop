"""Transactional settings dialog with left-side navigation."""

from copy import deepcopy

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)

from src.services.settings_service import SettingsService
from src.stores.settings_store import SettingsStore, get_settings_store
from src.ui.widgets.tabs.expert_tab import ExpertTab
from src.ui.widgets.tabs.pdf_output_tab import PDFOutputTab
from src.ui.widgets.tabs.processing_tab import ProcessingTab
from src.ui.widgets.tabs.provider_tab import ProviderTab
from src.ui.widgets.tabs.translation_tab import TranslationTab
from src.utils.file_utils import get_resource_path


class SettingsDialog(QDialog):
    """Edit a draft settings snapshot and commit only on Apply or OK."""

    settings_changed = Signal()

    PAGE_META = [
        ("模型与服务", "管理服务商、模型、API Key 与接口地址"),
        ("翻译质量", "默认语言、请求节奏、术语提取与提示词"),
        ("PDF 输出", "默认文件、水印、双语顺序与兼容策略"),
        ("文档处理", "OCR、公式、行处理、字体与内容保护"),
        ("高级设置", "线程、布局服务、输出目录与工作目录"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.committed_settings_store = get_settings_store()
        self.settings_store = SettingsStore(
            SettingsService(
                deepcopy(self.committed_settings_store.get_settings()), persist=False
            )
        )
        self.setup_ui()
        self._load_style()

    def setup_ui(self) -> None:
        self.setObjectName("settings_dialog")
        self.setWindowTitle("BabelDOC 设置")
        self.setMinimumSize(960, 640)
        self.resize(1080, 740)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        body = QFrame()
        body.setObjectName("settings_body")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        navigation = QFrame()
        navigation.setObjectName("settings_navigation")
        navigation.setFixedWidth(228)
        nav_layout = QVBoxLayout(navigation)
        nav_layout.setContentsMargins(20, 24, 20, 20)
        nav_layout.setSpacing(14)

        nav_title = QLabel("设置")
        nav_title.setObjectName("settings_nav_title")
        nav_layout.addWidget(nav_title)
        nav_copy = QLabel("配置默认行为与异常文档的恢复选项。")
        nav_copy.setObjectName("settings_nav_copy")
        nav_copy.setWordWrap(True)
        nav_layout.addWidget(nav_copy)

        self.navigation_list = QListWidget()
        self.navigation_list.setObjectName("settings_nav_list")
        self.navigation_list.setSpacing(4)
        for title, _subtitle in self.PAGE_META:
            self.navigation_list.addItem(QListWidgetItem(title))
        nav_layout.addWidget(self.navigation_list, 1)

        local_note = QLabel("所有设置保存在本机配置文件中")
        local_note.setObjectName("settings_local_note")
        local_note.setWordWrap(True)
        nav_layout.addWidget(local_note)
        body_layout.addWidget(navigation)

        content = QFrame()
        content.setObjectName("settings_content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 20)
        content_layout.setSpacing(16)

        self.page_title = QLabel()
        self.page_title.setObjectName("settings_page_title")
        content_layout.addWidget(self.page_title)
        self.page_subtitle = QLabel()
        self.page_subtitle.setObjectName("settings_page_subtitle")
        self.page_subtitle.setWordWrap(True)
        content_layout.addWidget(self.page_subtitle)

        self.stack = QStackedWidget()
        self.stack.setObjectName("settings_stack")
        self.tabs = self.stack

        self.provider_tab = ProviderTab(self.settings_store)
        self.translation_tab = TranslationTab(self.settings_store)
        self.pdf_tab = PDFOutputTab(self.settings_store)
        self.processing_tab = ProcessingTab(self.settings_store)
        self.expert_tab = ExpertTab(self.settings_store)
        for page in (
            self.provider_tab,
            self.translation_tab,
            self.pdf_tab,
            self.processing_tab,
            self.expert_tab,
        ):
            self.stack.addWidget(page)
        content_layout.addWidget(self.stack, 1)
        body_layout.addWidget(content, 1)
        layout.addWidget(body, 1)

        footer = QFrame()
        footer.setObjectName("dialog_footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 14, 20, 14)
        footer_layout.setSpacing(10)
        footer_layout.addStretch()

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setObjectName("default_button")
        self.cancel_button.setMinimumSize(92, 38)
        self.cancel_button.clicked.connect(self.reject)
        footer_layout.addWidget(self.cancel_button)

        self.apply_button = QPushButton("应用")
        self.apply_button.setObjectName("secondary_button")
        self.apply_button.setMinimumSize(92, 38)
        self.apply_button.clicked.connect(self._on_apply)
        footer_layout.addWidget(self.apply_button)

        self.ok_button = QPushButton("保存设置")
        self.ok_button.setObjectName("primary_button")
        self.ok_button.setMinimumSize(112, 38)
        self.ok_button.clicked.connect(self._on_ok)
        footer_layout.addWidget(self.ok_button)
        layout.addWidget(footer)

        self.navigation_list.currentRowChanged.connect(self._select_page)
        self.navigation_list.setCurrentRow(0)

    def _select_page(self, index: int) -> None:
        if index < 0 or index >= len(self.PAGE_META):
            return
        self.stack.setCurrentIndex(index)
        title, subtitle = self.PAGE_META[index]
        self.page_title.setText(title)
        self.page_subtitle.setText(subtitle)

    def _load_style(self) -> None:
        style_path = get_resource_path("src/ui/styles/modern.qss")
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.load_settings()

    def _on_apply(self) -> bool:
        try:
            self.save_settings()
            committed = deepcopy(self.settings_store.get_settings())
            model_ids = [
                model.id
                for provider in committed.providers.providers
                for model in provider.models
            ]
            if committed.providers.selected_model_id not in model_ids:
                committed.providers.selected_model_id = (
                    model_ids[0] if model_ids else ""
                )
            self.committed_settings_store.replace_settings(committed)
        except Exception as exc:
            QMessageBox.critical(self, "保存失败", f"设置未保存：{exc}")
            return False
        self.settings_changed.emit()
        return True

    def _on_ok(self) -> None:
        if self._on_apply():
            self.accept()

    def load_settings(self) -> None:
        self.settings_store.replace_settings(
            deepcopy(self.committed_settings_store.get_settings())
        )
        self.provider_tab.load_providers()
        self.translation_tab.load_settings()
        self.pdf_tab.load_settings()
        self.processing_tab.load_settings()
        self.expert_tab.load_settings()

    def save_settings(self) -> None:
        self.translation_tab.save_settings()
        self.pdf_tab.save_settings()
        self.processing_tab.save_settings()
        self.expert_tab.save_settings()
