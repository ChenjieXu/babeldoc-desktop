import time
import asyncio
import threading
import unittest
from pathlib import Path
from unittest import mock

from PySide6.QtCore import QObject, Signal

from src.models.settings import (
    ModelConfig,
    PDFSettings,
    PathSettings,
    RPCSettings,
    Settings,
    TermExtractionSettings,
    TranslationSettings,
)
from src.models.translation import RuntimeOverrides, TranslationConfig, UploadedFile
from src.services.translation_request_factory import build_translation_request
from src.services.translation_service import _DocLayoutModelLoader, TranslationWorker
from src.stores.translation_store import TranslationStore, result_files_from_payload


class TranslationRequestMappingTests(unittest.TestCase):
    def test_default_output_directory_follows_source_pdf(self):
        settings = Settings()
        model = ModelConfig(
            id="model-id",
            display_name="Model",
            model_name="main-model",
            api_key="main-key",
        )
        source_dir = Path("tmp") / "babeldoc-source"
        source_file = source_dir / "input.pdf"
        file = UploadedFile(
            id="f",
            name="input.pdf",
            path=str(source_file),
            size=1,
        )

        request = build_translation_request(
            settings=settings,
            model=model,
            file=file,
            runtime=RuntimeOverrides(lang_in="en", lang_out="zh", pages=None, qps=4),
        )

        self.assertEqual(Path(request.output_dir), source_dir.absolute())

    def test_request_rejects_configuration_without_pdf_output(self):
        with self.assertRaisesRegex(ValueError, "至少需要启用一种"):
            TranslationConfig(
                input_file="input.pdf",
                lang_in="en",
                lang_out="zh",
                model="model",
                api_key="key",
                output_dual=False,
                output_mono=False,
            )

    def test_runtime_controls_and_advanced_settings_reach_request(self):
        output_dir = str(Path("tmp") / "out")
        working_dir = str(Path("tmp") / "work")
        settings = Settings(
            translation=TranslationSettings(
                lang_in="en",
                lang_out="zh",
                qps=4,
                min_text_length=9,
                pool_max_workers=7,
                term_pool_max_workers=3,
                custom_system_prompt="Be precise",
                auto_extract_glossary=False,
                add_formula_placehold_hint=True,
                ignore_cache=True,
                save_auto_extracted_glossary=True,
            ),
            pdf=PDFSettings(
                output_dual=False,
                output_mono=True,
                watermark_mode="both",
                skip_clean=True,
                dual_translate_first=True,
                disable_rich_text_translate=True,
                enhance_compatibility=True,
                use_alternating_pages_dual=True,
                max_pages_per_part=12,
                skip_scanned_detection=True,
                ocr_workaround=True,
                auto_enable_ocr_workaround=True,
                split_short_lines=True,
                short_line_split_factor=0.55,
                primary_font_family="serif",
                formular_font_pattern="math-font",
                formular_char_pattern="xyz",
                skip_form_render=True,
                skip_curve_render=True,
                only_parse_generate_pdf=True,
                remove_non_formula_lines=True,
                non_formula_line_iou_threshold=0.45,
                figure_table_protection_threshold=0.65,
                only_include_translated_page=True,
                merge_alternating_line_numbers=True,
            ),
            paths=PathSettings(
                output_dir=output_dir,
                working_dir=working_dir,
                glossary_files="/tmp/a.csv,/tmp/b.csv",
            ),
            rpc=RPCSettings(doclayout_host="http://layout:8000"),
            term_extraction=TermExtractionSettings(
                use_separate_config=True,
                custom_api_key="term-key",
                custom_base_url="https://term.invalid/v1",
                custom_model="term-model",
                reasoning="high",
            ),
        )
        model = ModelConfig(
            id="model-id",
            display_name="Model",
            model_name="main-model",
            api_key="main-key",
            base_url="https://main.invalid/v1",
            enable_json_mode=True,
            send_dashscope_header=True,
            no_send_temperature=True,
        )
        file = UploadedFile(id="f", name="input.pdf", path="/tmp/input.pdf", size=1)

        request = build_translation_request(
            settings=settings,
            model=model,
            file=file,
            runtime=RuntimeOverrides(
                lang_in="ja",
                lang_out="de",
                pages="1-5",
                qps=19,
                output_dual=True,
                output_mono=False,
                use_alternating_pages_dual=False,
                dual_translate_first=False,
                auto_extract_glossary=True,
                glossary_files="/tmp/task.csv",
            ),
        )

        self.assertEqual((request.lang_in, request.lang_out), ("ja", "de"))
        self.assertEqual(request.pages, "1-5")
        self.assertEqual(request.qps, 19)
        self.assertEqual(request.output_dir, output_dir)
        self.assertEqual(request.working_dir, working_dir)
        self.assertEqual(request.glossary_files, "/tmp/task.csv")
        self.assertTrue(request.output_dual)
        self.assertFalse(request.output_mono)
        self.assertFalse(request.use_alternating_pages_dual)
        self.assertFalse(request.dual_translate_first)
        self.assertTrue(request.auto_extract_glossary)
        self.assertEqual(request.custom_system_prompt, "Be precise")
        self.assertEqual(request.max_pages_per_part, 12)
        self.assertTrue(request.skip_scanned_detection)
        self.assertTrue(request.only_parse_generate_pdf)
        self.assertEqual(request.doclayout_host, "http://layout:8000")
        self.assertTrue(request.term_extraction_use_separate_config)
        self.assertEqual(request.term_extraction_model, "term-model")
        self.assertEqual(request.term_extraction_api_key, "term-key")

    def test_babeldoc_constructor_receives_supported_fields(self):
        request = TranslationConfig(
            input_file="input.pdf",
            lang_in="en",
            lang_out="zh",
            model="model",
            api_key="key",
            pages="2-3",
            output_dir="out",
            working_dir="work",
            watermark_mode="both",
            qps=8,
            min_text_length=7,
            custom_system_prompt="prompt",
            max_pages_per_part=10,
            skip_form_render=True,
            only_include_translated_page=True,
        )
        worker = TranslationWorker(request)

        class FakeTranslator:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeBabelConfig:
            @staticmethod
            def create_max_pages_per_part_split_strategy(value):
                return ("split", value)

            def __init__(self, **kwargs):
                self.kwargs = kwargs

        class FakeWatermark:
            Watermarked = "watermarked"
            NoWatermark = "no_watermark"
            Both = "both"

        worker._OpenAITranslator = FakeTranslator
        worker._TranslationConfig = FakeBabelConfig
        worker._WatermarkOutputMode = FakeWatermark
        worker._set_translate_rate_limiter = mock.Mock()
        worker.doc_layout_model = object()

        with mock.patch.object(worker, "_load_glossaries", return_value=["glossary"]):
            built = worker._build_babeldoc_config()

        self.assertEqual(built.kwargs["pages"], "2-3")
        self.assertEqual(built.kwargs["output_dir"], "out")
        self.assertEqual(built.kwargs["working_dir"], "work")
        self.assertEqual(built.kwargs["watermark_output_mode"], "both")
        self.assertEqual(built.kwargs["qps"], 8)
        self.assertEqual(built.kwargs["min_text_length"], 7)
        self.assertEqual(built.kwargs["custom_system_prompt"], "prompt")
        self.assertEqual(built.kwargs["split_strategy"], ("split", 10))
        self.assertTrue(built.kwargs["skip_form_render"])
        self.assertTrue(built.kwargs["only_include_translated_page"])
        self.assertEqual(built.kwargs["glossaries"], ["glossary"])
        worker._set_translate_rate_limiter.assert_called_once_with(8)


class ResultAndCancellationTests(unittest.TestCase):
    def test_both_watermark_mode_keeps_all_distinct_results(self):
        files = result_files_from_payload(
            {
                "monoPdfPath": "/tmp/watermarked.mono.pdf",
                "dualPdfPath": "/tmp/watermarked.dual.pdf",
                "noWatermarkMonoPdfPath": "/tmp/plain.mono.pdf",
                "noWatermarkDualPdfPath": "/tmp/plain.dual.pdf",
            }
        )

        self.assertEqual(len(files), 4)
        self.assertEqual(
            [file.file_type for file in files],
            ["单语 PDF", "双语 PDF", "无水印单语 PDF", "无水印双语 PDF"],
        )

    def test_duplicate_no_watermark_aliases_are_not_shown_twice(self):
        files = result_files_from_payload(
            {
                "monoPdfPath": "/tmp/mono.pdf",
                "noWatermarkMonoPdfPath": "/tmp/mono.pdf",
            }
        )
        self.assertEqual(len(files), 1)

    def test_cancel_request_is_non_blocking_and_cooperative(self):
        request = TranslationConfig(
            input_file="input.pdf",
            lang_in="en",
            lang_out="zh",
            model="model",
            api_key="key",
        )
        worker = TranslationWorker(request)
        babeldoc_config = mock.Mock()
        worker._babeldoc_config = babeldoc_config

        started = time.monotonic()
        worker.request_cancel()

        self.assertLess(time.monotonic() - started, 0.1)
        self.assertTrue(worker._cancel_requested.is_set())
        babeldoc_config.cancel_translation.assert_called_once_with()

    def test_worker_can_exit_cooperatively_without_terminate(self):
        request = TranslationConfig(
            input_file="input.pdf",
            lang_in="en",
            lang_out="zh",
            model="model",
            api_key="key",
        )

        class WaitingWorker(TranslationWorker):
            async def _run_async(self):
                while not self._cancel_requested.is_set():
                    await asyncio.sleep(0.01)

        worker = WaitingWorker(request)
        worker.start()
        self.assertTrue(worker.isRunning())
        worker.request_cancel()
        self.assertTrue(worker.wait(1000))
        self.assertFalse(worker.isRunning())

    def test_cancel_interrupts_wait_for_onnx_initialization(self):
        started = threading.Event()
        release = threading.Event()

        class SlowModel:
            @staticmethod
            def load_onnx():
                started.set()
                release.wait(5)
                return object()

        request = TranslationConfig(
            input_file="input.pdf",
            lang_in="en",
            lang_out="zh",
            model="model",
            api_key="key",
        )

        class InitializingWorker(TranslationWorker):
            async def _run_async(self):
                self._DocLayoutModel = SlowModel
                await self._load_onnx_model()

        worker = InitializingWorker(request, model_loader=_DocLayoutModelLoader())
        try:
            worker.start()
            self.assertTrue(started.wait(1))
            worker.request_cancel()
            self.assertTrue(worker.wait(1000))
        finally:
            release.set()

    def test_cancelled_and_next_worker_share_one_onnx_load(self):
        started = threading.Event()
        release = threading.Event()
        calls = []

        class SlowModel:
            @staticmethod
            def load_onnx():
                calls.append(True)
                started.set()
                release.wait(5)
                return "layout-model"

        request = TranslationConfig(
            input_file="input.pdf",
            lang_in="en",
            lang_out="zh",
            model="model",
            api_key="key",
        )
        shared_loader = _DocLayoutModelLoader()

        class InitializingWorker(TranslationWorker):
            async def _run_async(self):
                self._DocLayoutModel = SlowModel
                self.loaded_model = await self._load_onnx_model()

        first = InitializingWorker(request, model_loader=shared_loader)
        second = InitializingWorker(request, model_loader=shared_loader)
        try:
            first.start()
            self.assertTrue(started.wait(1))
            first.request_cancel()
            self.assertTrue(first.wait(1000))

            second.start()
            time.sleep(0.1)
            self.assertEqual(len(calls), 1)
            release.set()
            self.assertTrue(second.wait(1000))
            self.assertEqual(second.loaded_model, "layout-model")
            self.assertEqual(len(calls), 1)
        finally:
            release.set()


class TranslationStoreOrchestrationTests(unittest.TestCase):
    class FakeService(QObject):
        progress_update = Signal(str, int, int, int)
        error_occurred = Signal(str)
        translation_finished = Signal(dict)
        log_message = Signal(str)
        worker_finished = Signal()

        def __init__(self):
            super().__init__()
            self.started = []
            self.cancel_requested = False

        def start_translation(self, request):
            self.started.append(request)

        def cancel_translation(self):
            self.cancel_requested = True

    @staticmethod
    def _request(name: str) -> TranslationConfig:
        return TranslationConfig(
            input_file=f"/tmp/{name}.pdf",
            lang_in="en",
            lang_out="zh",
            model="model",
            api_key="key",
        )

    def test_store_owns_sequential_batch_and_result_reduction(self):
        service = self.FakeService()
        with mock.patch(
            "src.stores.translation_store.get_translation_service",
            return_value=service,
        ):
            store = TranslationStore()

        completed = []
        store.batch_finished.connect(completed.append)
        store.start_batch([self._request("one"), self._request("two")])
        self.assertTrue(store.is_running)
        self.assertEqual(len(service.started), 1)

        service.translation_finished.emit({"monoPdfPath": "/tmp/one.mono.pdf"})
        service.worker_finished.emit()
        self.assertEqual(len(service.started), 2)
        self.assertTrue(store.is_running)

        service.translation_finished.emit({"dualPdfPath": "/tmp/two.dual.pdf"})
        service.worker_finished.emit()
        self.assertFalse(store.is_running)
        self.assertEqual(completed, [2])
        self.assertEqual(len(store.result_files), 2)

    def test_store_waits_for_worker_before_finishing_cancel(self):
        service = self.FakeService()
        with mock.patch(
            "src.stores.translation_store.get_translation_service",
            return_value=service,
        ):
            store = TranslationStore()

        cancelled = []
        store.cancellation_finished.connect(lambda: cancelled.append(True))
        store.start_batch([self._request("one")])
        store.cancel_batch()

        self.assertTrue(service.cancel_requested)
        self.assertTrue(store.is_running)
        service.worker_finished.emit()
        self.assertFalse(store.is_running)
        self.assertEqual(cancelled, [True])

    def _store_with_service(self):
        service = self.FakeService()
        with mock.patch(
            "src.stores.translation_store.get_translation_service",
            return_value=service,
        ):
            return TranslationStore(), service

    def test_error_dominates_late_finish_event(self):
        store, service = self._store_with_service()
        completed = []
        store.batch_finished.connect(completed.append)
        store.start_batch([self._request("one")])

        service.error_occurred.emit("provider failed")
        service.translation_finished.emit({"monoPdfPath": "/tmp/wrong.pdf"})
        service.worker_finished.emit()

        self.assertFalse(store.is_running)
        self.assertEqual(store.error, "provider failed")
        self.assertEqual(store.result_files, [])
        self.assertEqual(completed, [])

    def test_error_after_finish_still_fails_closed(self):
        store, service = self._store_with_service()
        store.start_batch([self._request("one")])

        service.translation_finished.emit({"monoPdfPath": "/tmp/wrong.pdf"})
        service.error_occurred.emit("late failure")
        service.worker_finished.emit()

        self.assertFalse(store.is_running)
        self.assertEqual(store.error, "late failure")
        self.assertEqual(store.result_files, [])

    def test_worker_exit_without_terminal_event_fails_closed(self):
        store, service = self._store_with_service()
        store.start_batch([self._request("one")])

        service.worker_finished.emit()

        self.assertFalse(store.is_running)
        self.assertIn("异常结束", store.error)


if __name__ == "__main__":
    unittest.main()
