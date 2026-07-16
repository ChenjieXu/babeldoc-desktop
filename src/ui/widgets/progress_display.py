"""
进度显示组件
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
    QPushButton,
    QScrollArea,
)
from src.stores.translation_store import get_translation_store


class ProgressDisplay(QWidget):
    """进度显示组件"""

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

        # 进度卡片
        self.progress_card = QFrame()
        self.progress_card.setObjectName("card_progress")

        card_layout = QVBoxLayout(self.progress_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(12)

        # 标题栏
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)

        title_label = QLabel("翻译进度")
        title_label.setObjectName("card_title")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.progress_percent_label = QLabel("0%")
        self.progress_percent_label.setObjectName("accent_label")
        header_layout.addWidget(self.progress_percent_label)

        card_layout.addLayout(header_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("translation_progress")
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        card_layout.addWidget(self.progress_bar)

        # 阶段信息
        self.stage_label = QLabel()
        self.stage_label.setObjectName("stage_label")
        card_layout.addWidget(self.stage_label)

        # 错误信息
        self.error_label = QLabel()
        self.error_label.setObjectName("error_chip")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        card_layout.addWidget(self.error_label)

        # 日志折叠按钮
        self.logs_button = QPushButton("详细日志")
        self.logs_button.setObjectName("ghost_button")
        self.logs_button.setCheckable(True)
        self.logs_button.setVisible(False)
        self.logs_button.clicked.connect(self._toggle_logs)
        card_layout.addWidget(self.logs_button)

        # 日志容器
        self.logs_container = QFrame()
        self.logs_container.setObjectName("logs_container")
        self.logs_container.setVisible(False)

        logs_layout = QVBoxLayout(self.logs_container)
        logs_layout.setContentsMargins(12, 12, 12, 12)
        logs_layout.setSpacing(4)

        # 日志滚动区域
        self.logs_scroll = QScrollArea()
        self.logs_scroll.setObjectName("logs_scroll")
        self.logs_scroll.setMaximumHeight(200)
        self.logs_scroll.setWidgetResizable(True)

        self.logs_widget = QWidget()
        self.logs_layout = QVBoxLayout(self.logs_widget)
        self.logs_layout.setContentsMargins(0, 0, 0, 0)
        self.logs_layout.setSpacing(2)
        self.logs_layout.addStretch()

        self.logs_scroll.setWidget(self.logs_widget)
        logs_layout.addWidget(self.logs_scroll)

        card_layout.addWidget(self.logs_container)

        layout.addWidget(self.progress_card)

    def setup_connections(self):
        """设置信号连接"""
        self.translation_store.is_running_changed.connect(self.on_state_changed)
        self.translation_store.progress_changed.connect(self.on_progress_changed)
        self.translation_store.stage_changed.connect(self.on_stage_changed)
        self.translation_store.stage_current_changed.connect(
            self.on_stage_progress_changed
        )
        self.translation_store.stage_total_changed.connect(
            self.on_stage_progress_changed
        )
        self.translation_store.error_occurred.connect(self.on_error_occurred)
        self.translation_store.log_message.connect(self.on_log_message)

    def update_visibility(self):
        """更新可见性"""
        is_running = self.translation_store.is_running
        progress = self.translation_store.progress

        show = is_running or progress > 0
        self.setVisible(show)

    def on_state_changed(self, is_running: bool):
        """运行状态改变"""
        self.update_visibility()

    def on_progress_changed(self, progress: int):
        """进度改变"""
        self.progress_bar.setValue(progress)
        self.progress_percent_label.setText(f"{progress}%")
        self.update_visibility()

    def on_stage_changed(self, stage: str):
        """阶段改变"""
        self._update_stage_info()

    def on_stage_progress_changed(self, _):
        """阶段进度改变"""
        self._update_stage_info()

    def _update_stage_info(self):
        """更新阶段信息"""
        stage = self.translation_store.stage
        current = self.translation_store.stage_current
        total = self.translation_store.stage_total

        if total > 0:
            text = f"{stage} ({current}/{total})"
        else:
            text = stage

        self.stage_label.setText(text)

    def on_error_occurred(self, error: str):
        """错误发生"""
        if error:
            self.error_label.setText(error)
            self.error_label.setVisible(True)
            self.progress_bar.setProperty("error", True)
        else:
            self.error_label.setVisible(False)
            self.progress_bar.setProperty("error", False)
        self.progress_bar.style().unpolish(self.progress_bar)
        self.progress_bar.style().polish(self.progress_bar)

    def on_log_message(self, message: str):
        """日志消息"""
        self.logs_button.setVisible(True)

        # 创建日志标签
        log_label = QLabel(message)
        log_label.setObjectName("log_line")
        log_label.setWordWrap(True)

        # 插入到最前面（显示最新的日志）
        self.logs_layout.insertWidget(self.logs_layout.count() - 1, log_label)

        # 限制日志数量（最多显示 50 条）
        while self.logs_layout.count() > 51:  # 50 + 1 (stretch)
            item = self.logs_layout.itemAt(0)
            if item and item.widget():
                item.widget().deleteLater()
                self.logs_layout.removeItem(item)

    def _toggle_logs(self):
        """切换日志显示"""
        self.logs_container.setVisible(self.logs_button.isChecked())

    def reset(self):
        """重置"""
        self.progress_bar.setValue(0)
        self.progress_percent_label.setText("0%")
        self.stage_label.setText("")
        self.error_label.setVisible(False)
        self.progress_bar.setProperty("error", False)
        self.logs_button.setVisible(False)
        self.logs_container.setVisible(False)
        self.logs_button.setChecked(False)

        # 清空日志
        for i in reversed(range(self.logs_layout.count() - 1)):  # 不删除 stretch
            item = self.logs_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
                self.logs_layout.removeItem(item)

        self.update_visibility()
