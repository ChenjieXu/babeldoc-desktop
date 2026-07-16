"""
翻译状态管理
"""

from threading import Lock
from enum import Enum, auto
from PySide6.QtCore import QObject, Signal
from typing import Optional, List
from src.models.translation import (
    UploadedFile,
    ResultFile,
    TranslationConfig,
)
from pathlib import Path
from src.services.translation_service import get_translation_service

# 日志最大条数
MAX_LOG_ENTRIES = 1000


class _WorkerOutcome(Enum):
    IDLE = auto()
    ACTIVE = auto()
    CANCELLING = auto()
    SUCCEEDED = auto()
    FAILED = auto()


def result_files_from_payload(result: dict) -> list[ResultFile]:
    """Convert every distinct BabelDOC output path into a UI-neutral model."""
    result_fields = (
        ("monoPdfPath", "单语 PDF"),
        ("dualPdfPath", "双语 PDF"),
        ("noWatermarkMonoPdfPath", "无水印单语 PDF"),
        ("noWatermarkDualPdfPath", "无水印双语 PDF"),
        ("autoExtractedGlossaryPath", "术语表 CSV"),
    )
    files = []
    seen = set()
    for key, file_type in result_fields:
        path = result.get(key)
        if not path or path in seen:
            continue
        seen.add(path)
        files.append(ResultFile(name=Path(path).name, path=path, file_type=file_type))
    return files


class TranslationStore(QObject):
    """翻译状态管理"""

    # 状态信号
    is_running_changed = Signal(bool)  # 运行状态改变
    progress_changed = Signal(int)  # 总体进度改变 (0-100)
    stage_changed = Signal(str)  # 当前阶段改变
    stage_current_changed = Signal(int)  # 当前阶段进度改变
    stage_total_changed = Signal(int)  # 当前阶段总数改变
    error_occurred = Signal(str)  # 错误发生
    result_added = Signal(str, str)  # 结果文件添加 (路径, 类型)
    result_files_changed = Signal()  # 结果文件列表改变
    log_message = Signal(str)  # 日志消息
    uploaded_files_changed = Signal()  # 上传文件列表改变
    batch_finished = Signal(int)  # 批次完成（文件数）
    cancellation_finished = Signal()
    batch_stopped = Signal()

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._progress = 0
        self._stage = ""
        self._stage_current = 0
        self._stage_total = 0
        self._error: Optional[str] = None
        self._uploaded_files: List[UploadedFile] = []
        self._result_files: List[ResultFile] = []
        self._logs: List[str] = []
        self._translation_service = get_translation_service()
        self._requests: List[TranslationConfig] = []
        self._current_request_index = 0
        self._worker_outcome = _WorkerOutcome.IDLE
        self._terminal_result: Optional[dict] = None
        self._connect_service()

    def _connect_service(self) -> None:
        self._translation_service.progress_update.connect(self._on_progress_update)
        self._translation_service.error_occurred.connect(self._on_service_error)
        self._translation_service.translation_finished.connect(
            self._on_translation_finished
        )
        self._translation_service.log_message.connect(self.add_log)
        self._translation_service.worker_finished.connect(self._on_worker_finished)

    # 状态属性
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._is_running

    @property
    def progress(self) -> int:
        """总体进度 (0-100)"""
        return self._progress

    @property
    def stage(self) -> str:
        """当前阶段"""
        return self._stage

    @property
    def stage_current(self) -> int:
        """当前阶段进度"""
        return self._stage_current

    @property
    def stage_total(self) -> int:
        """当前阶段总数"""
        return self._stage_total

    @property
    def error(self) -> Optional[str]:
        """错误信息"""
        return self._error

    @property
    def uploaded_files(self) -> List[UploadedFile]:
        """上传的文件列表"""
        return self._uploaded_files

    @property
    def result_files(self) -> List[ResultFile]:
        """结果文件列表"""
        return self._result_files

    @property
    def logs(self) -> List[str]:
        """日志列表"""
        return self._logs

    # 状态修改方法
    def set_is_running(self, running: bool) -> None:
        """设置运行状态"""
        if self._is_running != running:
            self._is_running = running
            self.is_running_changed.emit(running)

    def set_progress(self, progress: int) -> None:
        """设置总体进度"""
        if self._progress != progress:
            self._progress = progress
            self.progress_changed.emit(progress)

    def set_stage(self, stage: str) -> None:
        """设置当前阶段"""
        if self._stage != stage:
            self._stage = stage
            self.stage_changed.emit(stage)

    def set_stage_current(self, current: int) -> None:
        """设置当前阶段进度"""
        if self._stage_current != current:
            self._stage_current = current
            self.stage_current_changed.emit(current)

    def set_stage_total(self, total: int) -> None:
        """设置当前阶段总数"""
        if self._stage_total != total:
            self._stage_total = total
            self.stage_total_changed.emit(total)

    def set_error(self, error: Optional[str]) -> None:
        """设置错误信息"""
        if self._error != error:
            self._error = error
            if error:
                self.error_occurred.emit(error)

    def add_uploaded_file(self, file: UploadedFile) -> None:
        """添加上传的文件"""
        self._uploaded_files.append(file)
        self.uploaded_files_changed.emit()

    def remove_uploaded_file(self, file_id: str) -> None:
        """移除上传的文件"""
        self._uploaded_files = [f for f in self._uploaded_files if f.id != file_id]
        self.uploaded_files_changed.emit()

    def clear_uploaded_files(self) -> None:
        """清空上传的文件"""
        self._uploaded_files.clear()
        self.uploaded_files_changed.emit()

    def add_result_file(self, file: ResultFile) -> None:
        """添加结果文件"""
        self._result_files.append(file)
        self.result_added.emit(file.path, file.file_type)
        self.result_files_changed.emit()

    def clear_result_files(self) -> None:
        """清空结果文件"""
        self._result_files.clear()
        self.result_files_changed.emit()

    def add_log(self, message: str) -> None:
        """添加日志（限制最大条数）"""
        self._logs.append(message)
        # 限制日志大小，超出时移除最旧的
        if len(self._logs) > MAX_LOG_ENTRIES:
            self._logs = self._logs[-MAX_LOG_ENTRIES:]
        self.log_message.emit(message)

    def clear_logs(self) -> None:
        """清空日志"""
        self._logs.clear()

    def start_batch(self, requests: List[TranslationConfig]) -> None:
        """Start a sequential translation batch through the service layer."""
        if self.is_running:
            raise RuntimeError("翻译任务正在运行")
        if not requests:
            raise ValueError("翻译请求不能为空")

        self._requests = list(requests)
        self._current_request_index = 0
        self._worker_outcome = _WorkerOutcome.IDLE
        self._terminal_result = None
        self.set_error(None)
        self.set_progress(0)
        self.set_is_running(True)
        self._start_current_request()

    def _start_current_request(self) -> None:
        request = self._requests[self._current_request_index]
        self._worker_outcome = _WorkerOutcome.ACTIVE
        self._terminal_result = None
        self.set_stage(
            f"翻译文件 {self._current_request_index + 1}/"
            f"{len(self._requests)}: {Path(request.input_file).name}"
        )
        try:
            self._translation_service.start_translation(request)
        except Exception as exc:
            self._worker_outcome = _WorkerOutcome.IDLE
            self.set_is_running(False)
            self._requests = []
            self.set_error(f"翻译启动失败: {exc}")
            self.batch_stopped.emit()

    def cancel_batch(self) -> None:
        if not self.is_running or self._worker_outcome is _WorkerOutcome.CANCELLING:
            return
        self._worker_outcome = _WorkerOutcome.CANCELLING
        self._terminal_result = None
        self.set_stage("正在取消...")
        self._translation_service.cancel_translation()

    def _on_progress_update(
        self, stage: str, progress: int, current: int, total: int
    ) -> None:
        self.set_progress(progress)
        self.set_stage(stage)
        self.set_stage_current(current)
        self.set_stage_total(total)

    def _on_service_error(self, error: str) -> None:
        if self._worker_outcome in (
            _WorkerOutcome.IDLE,
            _WorkerOutcome.CANCELLING,
        ):
            return
        self._worker_outcome = _WorkerOutcome.FAILED
        self._terminal_result = None
        self.set_error(error)

    def _on_translation_finished(self, result: dict) -> None:
        if self._worker_outcome in (
            _WorkerOutcome.IDLE,
            _WorkerOutcome.CANCELLING,
            _WorkerOutcome.FAILED,
        ):
            return
        self._worker_outcome = _WorkerOutcome.SUCCEEDED
        self._terminal_result = result

    def _on_worker_finished(self) -> None:
        outcome = self._worker_outcome
        result = self._terminal_result
        self._worker_outcome = _WorkerOutcome.IDLE
        self._terminal_result = None

        if outcome is _WorkerOutcome.CANCELLING:
            self.set_is_running(False)
            self.set_stage("已取消")
            self.cancellation_finished.emit()
            self.batch_stopped.emit()
        elif outcome is _WorkerOutcome.FAILED:
            self.set_is_running(False)
            self.batch_stopped.emit()
        elif outcome is _WorkerOutcome.SUCCEEDED:
            for result_file in result_files_from_payload(result or {}):
                self.add_result_file(result_file)
            self._current_request_index += 1
            if self._current_request_index < len(self._requests):
                self._start_current_request()
                return
            total = len(self._requests)
            self.set_progress(100)
            self.set_stage("全部完成")
            self.set_is_running(False)
            self.batch_finished.emit(total)
            self.batch_stopped.emit()
        elif outcome is _WorkerOutcome.ACTIVE:
            self.set_error("翻译进程异常结束，未返回完成或错误事件")
            self.set_is_running(False)
            self.batch_stopped.emit()

    def reset(self) -> None:
        """重置状态"""
        self._requests = []
        self._current_request_index = 0
        self._worker_outcome = _WorkerOutcome.IDLE
        self._terminal_result = None
        self.set_is_running(False)
        self.set_progress(0)
        self.set_stage("")
        self.set_stage_current(0)
        self.set_stage_total(0)
        self.set_error(None)
        self.clear_result_files()
        self.clear_logs()


# 全局单例
_translation_store: Optional[TranslationStore] = None
_store_lock = Lock()  # 单例线程安全锁


def get_translation_store() -> TranslationStore:
    """获取翻译状态管理单例（线程安全）"""
    global _translation_store
    if _translation_store is None:
        with _store_lock:
            if _translation_store is None:
                _translation_store = TranslationStore()
    return _translation_store
