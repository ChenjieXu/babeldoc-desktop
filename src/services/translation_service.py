"""BabelDOC translation execution and worker lifecycle management."""

import asyncio
import logging
import threading
import traceback
from concurrent.futures import Future
from pathlib import Path
from threading import Lock
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal

from src.models.translation import TranslationConfig


# BabelDOC/OpenCV can use deep native/Python call stacks on complex documents.
threading.stack_size(16 * 1024 * 1024)
logger = logging.getLogger(__name__)


class _DocLayoutModelLoader:
    """Own and reuse the single process-wide local layout-model load."""

    def __init__(self):
        self._lock = Lock()
        self._future: Optional[Future] = None
        self._thread: Optional[threading.Thread] = None

    def get_future(self, load_callable) -> Future:
        with self._lock:
            if self._future is not None and self._future.done():
                if self._future.exception() is not None:
                    self._future = None
                    self._thread = None
            if self._future is None:
                future: Future = Future()

                def load() -> None:
                    try:
                        future.set_result(load_callable())
                    except BaseException as exc:
                        future.set_exception(exc)
                        logger.exception("ONNX 文档布局模型加载失败", exc_info=exc)

                self._future = future
                self._thread = threading.Thread(
                    target=load,
                    name="babeldoc-onnx-loader",
                    daemon=True,
                )
                self._thread.start()
            return self._future


_doc_layout_model_loader = _DocLayoutModelLoader()


class TranslationWorker(QThread):
    """Run one BabelDOC request outside the GUI thread."""

    progress_update = Signal(str, int, int, int)
    error_occurred = Signal(str)
    translation_finished = Signal(dict)
    log_message = Signal(str)

    def __init__(
        self,
        request: TranslationConfig,
        model_loader: Optional[_DocLayoutModelLoader] = None,
    ):
        super().__init__()
        self.request = request
        self._cancel_requested = threading.Event()
        self._babeldoc_config = None
        self._high_level = None
        self._TranslationConfig = None
        self._WatermarkOutputMode = None
        self._OpenAITranslator = None
        self._set_translate_rate_limiter = None
        self._DocLayoutModel = None
        self._RpcDocLayoutModel = None
        self.doc_layout_model = None
        self._model_loader = model_loader or _doc_layout_model_loader

    def run(self) -> None:
        try:
            asyncio.run(self._run_async())
        except asyncio.CancelledError:
            self.log_message.emit("翻译已取消")
        except Exception as exc:
            self.log_message.emit(f"详细错误:\n{traceback.format_exc()}")
            self.error_occurred.emit(f"翻译失败: {exc}\n\n请查看日志获取详细信息")
        finally:
            self._cleanup()

    async def _run_async(self) -> None:
        await self._initialize()
        self._raise_if_cancelled()
        await self._translate()

    def _raise_if_cancelled(self) -> None:
        if self._cancel_requested.is_set():
            raise asyncio.CancelledError("翻译已取消")

    async def _initialize(self) -> None:
        self.log_message.emit("正在加载翻译模块...")
        try:
            import babeldoc.format.pdf.high_level as high_level
            from babeldoc.docvision.doclayout import DocLayoutModel
            from babeldoc.format.pdf.translation_config import (
                TranslationConfig as BabelDocTranslationConfig,
            )
            from babeldoc.format.pdf.translation_config import WatermarkOutputMode
            from babeldoc.translator.translator import (
                OpenAITranslator,
                set_translate_rate_limiter,
            )

            self._high_level = high_level
            self._TranslationConfig = BabelDocTranslationConfig
            self._WatermarkOutputMode = WatermarkOutputMode
            self._OpenAITranslator = OpenAITranslator
            self._set_translate_rate_limiter = set_translate_rate_limiter
            self._DocLayoutModel = DocLayoutModel

            self.log_message.emit("步骤 1/4: BabelDOC 模块加载完成")
            self.log_message.emit("步骤 2/4: 初始化缓存目录...")
            high_level.init()
            self._raise_if_cancelled()

            if self.request.doclayout_host:
                from babeldoc.docvision.rpc_doclayout import RpcDocLayoutModel

                self._RpcDocLayoutModel = RpcDocLayoutModel
                self.doc_layout_model = RpcDocLayoutModel(
                    host=self.request.doclayout_host
                )
                self.log_message.emit("步骤 3/4: RPC 文档布局模型初始化完成")
            else:
                self.log_message.emit("步骤 3/4: 加载 ONNX 模型...")
                self.doc_layout_model = await self._load_onnx_model()
                self.log_message.emit("步骤 3/4: ONNX 模型加载完成")

            self._raise_if_cancelled()
            self.log_message.emit("步骤 4/4: 初始化完成")
        except ImportError as exc:
            self.log_message.emit(f"模块导入失败:\n{traceback.format_exc()}")
            raise RuntimeError(
                f"缺少必要的依赖库: {exc}\n\n请确保已正确安装 BabelDOC 及其依赖"
            ) from exc
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.log_message.emit(f"初始化失败:\n{traceback.format_exc()}")
            raise RuntimeError(
                f"初始化失败: {exc}\n\n请检查模型文件或 RPC 文档布局服务"
            ) from exc

    async def _load_onnx_model(self):
        """Await the shared ONNX load while allowing this consumer to cancel."""
        result = self._model_loader.get_future(self._DocLayoutModel.load_onnx)
        while not result.done():
            self._raise_if_cancelled()
            await asyncio.sleep(0.05)
        return result.result()

    def _build_translator(self, *, for_term_extraction: bool = False):
        request = self.request
        if for_term_extraction:
            model = request.term_extraction_model or request.model
            api_key = request.term_extraction_api_key or request.api_key
            base_url = request.term_extraction_base_url or request.base_url
            reasoning = request.term_extraction_reasoning or None
        else:
            model = request.model
            api_key = request.api_key
            base_url = request.base_url
            reasoning = None

        return self._OpenAITranslator(
            lang_in=request.lang_in,
            lang_out=request.lang_out,
            model=model,
            base_url=base_url,
            api_key=api_key,
            ignore_cache=request.ignore_cache,
            enable_json_mode_if_requested=request.enable_json_mode,
            send_dashscope_header=request.send_dashscope_header,
            send_temperature=not request.no_send_temperature,
            reasoning=reasoning,
        )

    def _load_glossaries(self) -> list:
        if not self.request.glossary_files:
            return []

        from babeldoc.glossary import Glossary

        loaded = []
        for raw_path in self.request.glossary_files.split(","):
            path = Path(raw_path.strip()).expanduser()
            if not path.is_file():
                self.log_message.emit(f"跳过不存在的术语表: {path}")
                continue
            try:
                glossary = Glossary.from_csv(path, self.request.lang_out)
            except Exception as exc:
                self.log_message.emit(f"术语表加载失败 {path}: {exc}")
                continue
            if glossary.entries:
                loaded.append(glossary)
        return loaded

    def _build_babeldoc_config(self):
        request = self.request
        translator = self._build_translator()
        term_translator = (
            self._build_translator(for_term_extraction=True)
            if request.term_extraction_use_separate_config
            else translator
        )
        self._set_translate_rate_limiter(request.qps)

        watermark_mode = {
            "watermarked": self._WatermarkOutputMode.Watermarked,
            "no_watermark": self._WatermarkOutputMode.NoWatermark,
            "both": self._WatermarkOutputMode.Both,
        }.get(request.watermark_mode, self._WatermarkOutputMode.Watermarked)

        split_strategy = None
        if request.max_pages_per_part:
            split_strategy = (
                self._TranslationConfig.create_max_pages_per_part_split_strategy(
                    request.max_pages_per_part
                )
            )

        return self._TranslationConfig(
            input_file=request.input_file,
            translator=translator,
            term_extraction_translator=term_translator,
            doc_layout_model=self.doc_layout_model,
            lang_in=request.lang_in,
            lang_out=request.lang_out,
            pages=request.pages,
            output_dir=request.output_dir,
            working_dir=request.working_dir,
            no_dual=not request.output_dual,
            no_mono=not request.output_mono,
            watermark_output_mode=watermark_mode,
            qps=request.qps,
            min_text_length=request.min_text_length,
            pool_max_workers=request.pool_max_workers,
            term_pool_max_workers=request.term_pool_max_workers,
            custom_system_prompt=request.custom_system_prompt or None,
            auto_extract_glossary=request.auto_extract_glossary,
            save_auto_extracted_glossary=request.save_auto_extracted_glossary,
            add_formula_placehold_hint=request.add_formula_placehold_hint,
            skip_clean=request.skip_clean,
            dual_translate_first=request.dual_translate_first,
            disable_rich_text_translate=request.disable_rich_text_translate,
            enhance_compatibility=request.enhance_compatibility,
            use_alternating_pages_dual=request.use_alternating_pages_dual,
            split_strategy=split_strategy,
            skip_scanned_detection=request.skip_scanned_detection,
            ocr_workaround=request.ocr_workaround,
            auto_enable_ocr_workaround=request.auto_enable_ocr_workaround,
            split_short_lines=request.split_short_lines,
            short_line_split_factor=request.short_line_split_factor,
            primary_font_family=request.primary_font_family,
            formular_font_pattern=request.formular_font_pattern,
            formular_char_pattern=request.formular_char_pattern,
            skip_form_render=request.skip_form_render,
            skip_curve_render=request.skip_curve_render,
            only_parse_generate_pdf=request.only_parse_generate_pdf,
            remove_non_formula_lines=request.remove_non_formula_lines,
            non_formula_line_iou_threshold=request.non_formula_line_iou_threshold,
            figure_table_protection_threshold=(
                request.figure_table_protection_threshold
            ),
            only_include_translated_page=request.only_include_translated_page,
            merge_alternating_line_numbers=request.merge_alternating_line_numbers,
            glossaries=self._load_glossaries(),
        )

    async def _translate(self) -> None:
        self.log_message.emit("开始翻译...")
        self._babeldoc_config = self._build_babeldoc_config()
        if self._cancel_requested.is_set():
            self._babeldoc_config.cancel_translation()
            self._raise_if_cancelled()

        async for event in self._high_level.async_translate(self._babeldoc_config):
            if self._cancel_requested.is_set():
                self._babeldoc_config.cancel_translation()
                continue

            event_type = event.get("type")
            if event_type == "progress_update":
                self.progress_update.emit(
                    event.get("stage", ""),
                    int(event.get("overall_progress", 0)),
                    int(event.get("stage_current", 0)),
                    int(event.get("stage_total", 0)),
                )
            elif event_type == "error":
                self.error_occurred.emit(str(event.get("error", "Unknown error")))
            elif event_type == "finish":
                result = event.get("translate_result")
                self.translation_finished.emit(self._serialize_result(result))

        if self._cancel_requested.is_set():
            self.log_message.emit("翻译已取消")

    @staticmethod
    def _serialize_result(result) -> dict:
        def path_value(name: str):
            value = getattr(result, name, None) if result is not None else None
            return str(value) if value else None

        return {
            "originalPdfPath": path_value("original_pdf_path") or "",
            "totalSeconds": getattr(result, "total_seconds", 0) if result else 0,
            "monoPdfPath": path_value("mono_pdf_path"),
            "dualPdfPath": path_value("dual_pdf_path"),
            "noWatermarkMonoPdfPath": path_value("no_watermark_mono_pdf_path"),
            "noWatermarkDualPdfPath": path_value("no_watermark_dual_pdf_path"),
            "autoExtractedGlossaryPath": path_value("auto_extracted_glossary_path"),
        }

    def request_cancel(self) -> None:
        """Request cooperative cancellation without blocking the caller."""
        self._cancel_requested.set()
        if self._babeldoc_config is not None:
            self._babeldoc_config.cancel_translation()
        else:
            self.log_message.emit("正在取消初始化...")

    def _cleanup(self) -> None:
        self._babeldoc_config = None
        self.doc_layout_model = None
        self._high_level = None
        self._TranslationConfig = None
        self._WatermarkOutputMode = None
        self._OpenAITranslator = None
        self._set_translate_rate_limiter = None
        self._DocLayoutModel = None
        self._RpcDocLayoutModel = None


class TranslationService(QObject):
    """Own the single active worker and relay its signals."""

    progress_update = Signal(str, int, int, int)
    error_occurred = Signal(str)
    translation_finished = Signal(dict)
    log_message = Signal(str)
    worker_finished = Signal()

    def __init__(self):
        super().__init__()
        self._worker: Optional[TranslationWorker] = None
        self._lock = Lock()

    def start_translation(self, request: TranslationConfig) -> None:
        with self._lock:
            if self._worker is not None and self._worker.isRunning():
                raise RuntimeError("前一个翻译任务仍在结束，请稍候")

            worker = TranslationWorker(request)
            self._worker = worker
            worker.progress_update.connect(self.progress_update.emit)
            worker.error_occurred.connect(self.error_occurred.emit)
            worker.translation_finished.connect(self.translation_finished.emit)
            worker.log_message.connect(self.log_message.emit)
            worker.finished.connect(self._on_worker_finished)
            worker.start()

    def cancel_translation(self) -> None:
        """Request cancellation and return immediately to the GUI event loop."""
        with self._lock:
            worker = self._worker
        if worker is not None:
            worker.request_cancel()

    def _on_worker_finished(self) -> None:
        worker = self.sender()
        with self._lock:
            if worker is self._worker:
                self._worker = None
        if isinstance(worker, QObject):
            worker.deleteLater()
        self.worker_finished.emit()

    def is_running(self) -> bool:
        with self._lock:
            return self._worker is not None and self._worker.isRunning()


_translation_service: Optional[TranslationService] = None
_service_lock = Lock()


def get_translation_service() -> TranslationService:
    """Get the process-wide translation service."""
    global _translation_service
    if _translation_service is None:
        with _service_lock:
            if _translation_service is None:
                _translation_service = TranslationService()
    return _translation_service
