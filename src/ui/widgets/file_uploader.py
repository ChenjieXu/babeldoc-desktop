"""PDF upload and queue widget."""

from pathlib import Path
from typing import List
from uuid import uuid4

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.models.translation import UploadedFile
from src.stores.translation_store import get_translation_store
from src.utils.file_utils import (
    file_exists,
    format_file_size,
    get_file_info,
    is_pdf_file,
    select_files,
)

MAX_FILE_SIZE = 500 * 1024 * 1024


class UploadDropArea(QFrame):
    """Clickable drop surface that emits paths without owning validation."""

    clicked = Signal()
    files_dropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("upload_area")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.files_dropped.emit([path for path in paths if path])
        event.acceptProposedAction()


class FileUploader(QWidget):
    """Add, validate, display and remove PDFs from the translation queue."""

    files_changed = Signal()

    def __init__(self):
        super().__init__()
        self.translation_store = get_translation_store()
        self.setup_ui()
        self.setup_connections()
        self.update_file_list()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self.upload_area = self._create_upload_area()
        layout.addWidget(self.upload_area)

        self.file_list = QListWidget()
        self.file_list.setObjectName("file_queue")
        self.file_list.setSpacing(6)
        self.file_list.setSelectionMode(QListWidget.NoSelection)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.file_list)

    def _create_upload_area(self) -> UploadDropArea:
        area = UploadDropArea()
        area.setMinimumHeight(172)

        layout = QVBoxLayout(area)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(7)
        layout.setContentsMargins(24, 22, 24, 22)

        badge = QLabel("PDF")
        badge.setObjectName("upload_badge")
        badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(badge, 0, Qt.AlignCenter)

        title = QLabel("拖拽 PDF 到这里")
        title.setObjectName("upload_title")
        layout.addWidget(title, 0, Qt.AlignCenter)

        hint = QLabel("支持批量添加，也可以直接选择文件")
        hint.setObjectName("upload_hint")
        layout.addWidget(hint, 0, Qt.AlignCenter)

        self.browse_button = QPushButton("选择 PDF 文件")
        self.browse_button.setObjectName("secondary_button")
        self.browse_button.clicked.connect(self._choose_files)
        layout.addWidget(self.browse_button, 0, Qt.AlignCenter)

        area.clicked.connect(self._choose_files)
        area.files_dropped.connect(self._add_files)
        return area

    def setup_connections(self) -> None:
        self.translation_store.uploaded_files_changed.connect(self.update_file_list)

    def _choose_files(self) -> None:
        files = select_files(self, "PDF Files (*.pdf)", multiple=True)
        if files:
            self._add_files(files)

    def _add_files(self, file_paths: List[str]) -> None:
        for file_path in file_paths:
            try:
                if not file_exists(file_path):
                    QMessageBox.warning(
                        self, "文件不可用", f"找不到文件：{Path(file_path).name}"
                    )
                    continue
                if not is_pdf_file(file_path):
                    QMessageBox.warning(
                        self, "格式不支持", f"不是 PDF 文件：{Path(file_path).name}"
                    )
                    continue

                info = get_file_info(file_path)
                if info["size"] > MAX_FILE_SIZE:
                    QMessageBox.warning(
                        self,
                        "文件过大",
                        f"{Path(file_path).name} 超过 500 MB 限制。",
                    )
                    continue

                uploaded = UploadedFile(
                    id=str(uuid4()),
                    name=info["name"],
                    path=info["path"],
                    size=info["size"],
                )
                self.translation_store.add_uploaded_file(uploaded)
            except FileNotFoundError:
                QMessageBox.warning(
                    self, "文件不可用", f"找不到文件：{Path(file_path).name}"
                )
            except Exception as exc:
                QMessageBox.warning(self, "添加失败", f"无法添加文件：{exc}")

    def update_file_list(self) -> None:
        self.file_list.clear()
        files = self.translation_store.uploaded_files
        self.file_list.setVisible(bool(files))
        if not files:
            self.files_changed.emit()
            return

        for file in files:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, file.id)
            item.setSizeHint(QSize(0, 62))
            self.file_list.addItem(item)
            self.file_list.setItemWidget(item, self._create_file_item(file))

        visible_rows = min(len(files), 4)
        self.file_list.setFixedHeight(visible_rows * 68 + 4)
        self.files_changed.emit()

    def _create_file_item(self, file: UploadedFile) -> QFrame:
        item = QFrame()
        item.setObjectName("file_item")

        layout = QHBoxLayout(item)
        layout.setContentsMargins(12, 8, 10, 8)
        layout.setSpacing(10)

        badge = QLabel("PDF")
        badge.setObjectName("file_badge")
        badge.setAlignment(Qt.AlignCenter)
        layout.addWidget(badge)

        info = QVBoxLayout()
        info.setSpacing(2)
        name = QLabel(file.name)
        name.setObjectName("file_name")
        name.setToolTip(file.path)
        info.addWidget(name)
        meta = QLabel(format_file_size(file.size))
        meta.setObjectName("file_meta")
        info.addWidget(meta)
        layout.addLayout(info, 1)

        remove_button = QPushButton("移除")
        remove_button.setObjectName("file_remove_button")
        remove_button.setToolTip(f"从队列移除 {file.name}")
        remove_button.clicked.connect(lambda _checked=False: self._remove_file(file.id))
        layout.addWidget(remove_button)
        return item

    def _remove_file(self, file_id: str) -> None:
        self.translation_store.remove_uploaded_file(file_id)
