"""Main application workspace."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from src.stores.translation_store import get_translation_store
from src.ui.widgets.action_buttons import ActionButtons
from src.ui.widgets.app_header import AppHeader
from src.ui.widgets.app_sidebar import AppSidebar
from src.ui.widgets.file_uploader import FileUploader
from src.ui.widgets.progress_display import ProgressDisplay
from src.ui.widgets.results_display import ResultsDisplay
from src.ui.widgets.settings_dialog import SettingsDialog
from src.utils.file_utils import get_resource_path


class MainWindow(QMainWindow):
    """Coordinate the main translation workflow and its visible state."""

    def __init__(self):
        super().__init__()
        self.translation_store = get_translation_store()
        self._closing_after_cancel = False
        self.setup_ui()
        self.setup_connections()
        self.load_style()

    def setup_ui(self) -> None:
        self.setWindowTitle("BabelDOC Desktop")
        self.setMinimumSize(1000, 680)
        self.resize(1400, 900)

        central_widget = QWidget()
        central_widget.setObjectName("app_root")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = AppHeader()
        main_layout.addWidget(self.header)

        scroll = QScrollArea()
        scroll.setObjectName("workspace_scroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        page = QWidget()
        page.setObjectName("workspace_page")
        page.setMinimumWidth(940)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(28, 24, 28, 32)
        page_layout.setSpacing(20)

        intro = QVBoxLayout()
        intro.setSpacing(5)
        page_title = QLabel("开始一次 PDF 翻译")
        page_title.setObjectName("page_title")
        intro.addWidget(page_title)
        page_subtitle = QLabel(
            "添加文档并确认本次任务设置；兼容性、OCR 与性能选项可在设置中调整。"
        )
        page_subtitle.setObjectName("page_subtitle")
        intro.addWidget(page_subtitle)
        page_layout.addLayout(intro)

        workspace = QHBoxLayout()
        workspace.setSpacing(20)

        left_area = self._create_left_area()
        workspace.addWidget(left_area, 3)

        right_area = self._create_quick_settings_card()
        workspace.addWidget(right_area, 2)
        workspace.setAlignment(right_area, Qt.AlignTop)

        page_layout.addLayout(workspace)
        page_layout.addStretch()
        scroll.setWidget(page)
        main_layout.addWidget(scroll, 1)

        self.settings_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Preferences), self
        )
        self.settings_shortcut.activated.connect(self._open_settings_dialog)

    def _create_left_area(self) -> QWidget:
        left_area = QWidget()
        left_area.setObjectName("left_workspace")
        layout = QVBoxLayout(left_area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        upload_card = QFrame()
        upload_card.setObjectName("workspace_card")
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(20, 18, 20, 20)
        upload_layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        upload_title = QLabel("文档队列")
        upload_title.setObjectName("card_title")
        title_row.addWidget(upload_title)
        upload_badge = QLabel("PDF · 最多 500 MB / 个")
        upload_badge.setObjectName("neutral_chip")
        title_row.addWidget(upload_badge)
        title_row.addStretch()
        upload_layout.addLayout(title_row)

        self.file_uploader = FileUploader()
        upload_layout.addWidget(self.file_uploader)
        layout.addWidget(upload_card)

        self.activity_placeholder = QFrame()
        self.activity_placeholder.setObjectName("activity_placeholder")
        placeholder_layout = QVBoxLayout(self.activity_placeholder)
        placeholder_layout.setContentsMargins(20, 18, 20, 18)
        placeholder_layout.setSpacing(4)
        placeholder_title = QLabel("任务状态会显示在这里")
        placeholder_title.setObjectName("placeholder_title")
        placeholder_layout.addWidget(placeholder_title)
        placeholder_copy = QLabel(
            "开始翻译后可查看实时进度；完成后可直接打开输出位置。"
        )
        placeholder_copy.setObjectName("placeholder_copy")
        placeholder_copy.setWordWrap(True)
        placeholder_layout.addWidget(placeholder_copy)
        layout.addWidget(self.activity_placeholder)

        self.progress_display = ProgressDisplay()
        layout.addWidget(self.progress_display)

        self.results_display = ResultsDisplay()
        layout.addWidget(self.results_display)
        layout.addStretch()
        return left_area

    def _create_quick_settings_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("quick_settings_card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(16)

        title = QLabel("本次翻译")
        title.setObjectName("card_title_large")
        layout.addWidget(title)
        subtitle = QLabel("仅影响当前任务；更细的默认值和恢复选项在设置中。")
        subtitle.setObjectName("card_subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.sidebar = AppSidebar()
        layout.addWidget(self.sidebar)

        divider = QFrame()
        divider.setObjectName("section_divider")
        divider.setFrameShape(QFrame.HLine)
        layout.addWidget(divider)

        self.action_buttons = ActionButtons(
            runtime_config_provider=self.sidebar.get_config
        )
        layout.addWidget(self.action_buttons)
        return card

    def setup_connections(self) -> None:
        self.header.settings_requested.connect(self._open_settings_dialog)
        self.translation_store.batch_stopped.connect(self._finish_deferred_close)
        self.translation_store.is_running_changed.connect(
            self._update_activity_visibility
        )
        self.translation_store.progress_changed.connect(
            self._update_activity_visibility
        )
        self.translation_store.result_files_changed.connect(
            self._update_activity_visibility
        )
        self._update_activity_visibility()

    def _update_activity_visibility(self, _value=None) -> None:
        has_activity = (
            self.translation_store.is_running
            or self.translation_store.progress > 0
            or bool(self.translation_store.result_files)
        )
        self.activity_placeholder.setVisible(not has_activity)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Keep the window alive until cooperative cancellation completes."""
        if self.translation_store.is_running:
            self._closing_after_cancel = True
            self.setEnabled(False)
            self.translation_store.cancel_batch()
            event.ignore()
            return
        event.accept()

    def _finish_deferred_close(self) -> None:
        if not self._closing_after_cancel:
            return
        self._closing_after_cancel = False
        self.setEnabled(True)
        QTimer.singleShot(0, self.close)

    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(self)
        dialog.exec()

    def load_style(self) -> None:
        style_path = get_resource_path("src/ui/styles/modern.qss")
        if style_path.exists():
            self.setStyleSheet(style_path.read_text(encoding="utf-8"))
