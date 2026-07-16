"""
结果显示组件
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
)
from src.stores.translation_store import get_translation_store
from src.utils.file_utils import open_file_location


class ResultsDisplay(QWidget):
    """结果显示组件"""

    def __init__(self):
        super().__init__()
        self.translation_store = get_translation_store()
        self.setup_ui()
        self.setup_connections()
        self.update_visibility()

    def setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 结果卡片
        self.results_card = QFrame()
        self.results_card.setObjectName("card_results")

        card_layout = QVBoxLayout(self.results_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(16)

        # 标题栏
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_label = QLabel("翻译结果")
        title_label.setObjectName("card_title")
        header_layout.addWidget(title_label)

        self.count_label = QLabel("0 个文件")
        self.count_label.setObjectName("count_chip")
        header_layout.addWidget(self.count_label)

        header_layout.addStretch()

        card_layout.addLayout(header_layout)

        # 结果列表
        self.results_list = QFrame()
        results_list_layout = QVBoxLayout(self.results_list)
        results_list_layout.setContentsMargins(0, 0, 0, 0)
        results_list_layout.setSpacing(12)

        card_layout.addWidget(self.results_list)

        layout.addWidget(self.results_card)

    def setup_connections(self):
        """设置信号连接"""
        self.translation_store.result_files_changed.connect(self._sync_results)

    def update_visibility(self):
        """更新可见性"""
        has_results = len(self.translation_store.result_files) > 0
        self.setVisible(has_results)

    def _sync_results(self):
        """Rebuild the view from the store so clear/reset cannot leave stale rows."""
        layout = self.results_list.layout()
        for index in reversed(range(layout.count())):
            item = layout.takeAt(index)
            if item.widget():
                item.widget().deleteLater()

        for result in self.translation_store.result_files:
            self.add_result_file(
                {
                    "name": result.name,
                    "path": result.path,
                    "file_type": result.file_type,
                }
            )

        self.count_label.setText(f"{len(self.translation_store.result_files)} 个文件")
        self.update_visibility()

    def add_result_file(self, file: dict):
        """添加结果文件"""
        result_item = self._create_result_item(file)
        self.results_list.layout().addWidget(result_item)

        # 更新计数
        count = len(self.translation_store.result_files)
        self.count_label.setText(f"{count} 个文件")

        self.update_visibility()

    def _create_result_item(self, file: dict) -> QFrame:
        """创建结果项"""
        result_item = QFrame()
        result_item.setObjectName("result_item")

        layout = QHBoxLayout(result_item)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # 文件图标
        icon_label = QLabel(
            "[CSV]" if file.get("file_type") == "术语表 CSV" else "[PDF]"
        )
        icon_label.setObjectName("result_icon")
        layout.addWidget(icon_label)

        # 文件信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        name_label = QLabel(file.get("name", ""))
        name_label.setObjectName("result_name")
        info_layout.addWidget(name_label)

        # 文件类型标签
        file_type = file.get("file_type", "")
        type_label = QLabel(file_type)
        type_label.setObjectName("result_type")
        info_layout.addWidget(type_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # 打开位置按钮
        open_button = QPushButton("打开位置")
        open_button.setObjectName("ghost_button")
        open_button.clicked.connect(lambda: self._open_location(file.get("path", "")))
        layout.addWidget(open_button)

        return result_item

    def _open_location(self, path: str):
        """打开文件位置"""
        if not open_file_location(path):
            QMessageBox.warning(self, "警告", f"无法打开文件位置: {Path(path).name}")

    def clear_results(self):
        """清空结果"""
        layout = self.results_list.layout()
        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
                layout.removeItem(item)

        self.count_label.setText("0 个文件")
        self.update_visibility()
