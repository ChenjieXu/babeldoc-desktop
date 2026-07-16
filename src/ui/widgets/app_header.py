"""Application header for the desktop workspace."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.version import __version__


class AppHeader(QWidget):
    """Show product identity, runtime status and the settings entry point."""

    settings_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        self.setObjectName("app_header")
        self.setFixedHeight(76)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(14)

        logo_mark = QFrame()
        logo_mark.setObjectName("brand_mark")
        logo_mark.setFixedSize(38, 38)
        logo_layout = QVBoxLayout(logo_mark)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_label = QLabel("B")
        logo_label.setObjectName("brand_mark_text")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(logo_label)
        layout.addWidget(logo_mark)

        identity = QVBoxLayout()
        identity.setSpacing(1)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        title_label = QLabel("BabelDOC")
        title_label.setObjectName("header_title")
        title_row.addWidget(title_label)
        version_label = QLabel(f"v{__version__}")
        version_label.setObjectName("header_version")
        title_row.addWidget(version_label)
        title_row.addStretch()
        identity.addLayout(title_row)

        subtitle = QLabel("保留版式的智能 PDF 翻译工作台")
        subtitle.setObjectName("header_subtitle")
        identity.addWidget(subtitle)
        layout.addLayout(identity)
        layout.addStretch()

        status = QLabel("本地工作台")
        status.setObjectName("runtime_status")
        status.setFixedHeight(34)
        layout.addWidget(status, 0, Qt.AlignVCenter)

        self.settings_button = QPushButton("设置")
        self.settings_button.setObjectName("settings_button")
        self.settings_button.setFixedHeight(36)
        self.settings_button.setToolTip("打开设置（⌘/Ctrl + ,）")
        self.settings_button.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.settings_button, 0, Qt.AlignVCenter)
