"""Translation controls and request assembly."""

from typing import Callable, Optional

from PySide6.QtWidgets import QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from src.models.settings import ModelConfig
from src.models.translation import RuntimeOverrides
from src.services.translation_request_factory import build_translation_request
from src.stores.settings_store import get_settings_store
from src.stores.translation_store import get_translation_store


class ActionButtons(QWidget):
    """Issue commands to stores and render batch completion feedback."""

    def __init__(
        self,
        runtime_config_provider: Optional[Callable[[], RuntimeOverrides]] = None,
    ):
        super().__init__()
        self.translation_store = get_translation_store()
        self.settings_store = get_settings_store()
        self._runtime_config_provider = runtime_config_provider
        self.setup_ui()
        self.setup_connections()
        self.update_buttons()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.action_summary = QLabel()
        self.action_summary.setObjectName("action_summary")
        self.action_summary.setWordWrap(True)
        layout.addWidget(self.action_summary)

        self.start_button = QPushButton("开始翻译")
        self.start_button.setObjectName("start_button")
        self.start_button.setMinimumHeight(48)
        self.start_button.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.start_button)

        self.cancel_button = QPushButton("取消翻译")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setMinimumHeight(48)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        layout.addWidget(self.cancel_button)

    def setup_connections(self):
        self.translation_store.is_running_changed.connect(self.update_buttons)
        self.translation_store.uploaded_files_changed.connect(self.update_buttons)
        self.settings_store.selected_model_changed.connect(self.update_buttons)
        self.translation_store.error_occurred.connect(self._on_error_occurred)
        self.translation_store.batch_finished.connect(self._on_batch_finished)
        self.translation_store.cancellation_finished.connect(
            self._on_cancellation_finished
        )

    def update_buttons(self):
        is_running = self.translation_store.is_running
        has_files = bool(self.translation_store.uploaded_files)
        has_model = self.settings_store.get_selected_model() is not None

        self.start_button.setVisible(not is_running)
        self.start_button.setEnabled(has_files and has_model and not is_running)
        self.cancel_button.setVisible(is_running)
        self.cancel_button.setEnabled(is_running)

        if is_running:
            summary = "翻译进行中。你可以继续查看进度，或安全取消当前批次。"
        elif not has_model:
            summary = "先在设置中添加并选择一个模型。"
        elif not has_files:
            summary = "添加 PDF 后即可开始，任务会按队列顺序执行。"
        else:
            count = len(self.translation_store.uploaded_files)
            summary = f"已就绪：{count} 个文件将按当前配置依次翻译。"
        self.action_summary.setText(summary)

    def _current_runtime_config(self) -> RuntimeOverrides:
        if self._runtime_config_provider is None:
            settings = self.settings_store.get_settings().translation
            return RuntimeOverrides(
                lang_in=settings.lang_in,
                lang_out=settings.lang_out,
                pages=None,
                qps=settings.qps,
            )
        return self._runtime_config_provider()

    def _term_extraction_model(self) -> Optional[ModelConfig]:
        term = self.settings_store.get_settings().term_extraction
        if not term.model_config_id:
            return None
        for item in self.settings_store.get_all_models():
            model = item["model"]
            if model.id == term.model_config_id:
                return model
        return None

    def _on_start_clicked(self):
        model = self.settings_store.get_selected_model()
        if not model:
            QMessageBox.warning(self, "提示", "请先选择翻译模型")
            return

        files = self.translation_store.uploaded_files
        if not files:
            QMessageBox.warning(self, "提示", "请先上传 PDF 文件")
            return

        settings = self.settings_store.get_settings()
        runtime = self._current_runtime_config()
        term_model = self._term_extraction_model()
        requests = [
            build_translation_request(
                settings=settings,
                model=model,
                file=file,
                runtime=runtime,
                term_model=term_model,
            )
            for file in files
        ]
        try:
            self.translation_store.start_batch(requests)
        except Exception as exc:
            QMessageBox.critical(self, "错误", f"翻译失败: {exc}")

    def _on_cancel_clicked(self):
        self.cancel_button.setEnabled(False)
        self.translation_store.cancel_batch()

    def _on_error_occurred(self, error: str):
        QMessageBox.critical(self, "错误", error)

    def _on_batch_finished(self, total: int):
        QMessageBox.information(self, "成功", f"全部 {total} 个文件翻译完成！")

    def _on_cancellation_finished(self):
        QMessageBox.information(self, "提示", "翻译已取消")
