import os
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from src.models.settings import ModelConfig, Provider, Settings, create_default_settings
from src.models.translation import UploadedFile
from src.services.settings_service import SettingsService
from src.stores.settings_store import SettingsStore
from src.ui.widgets.app_sidebar import AppSidebar
from src.ui.widgets.file_uploader import FileUploader
from src.ui.widgets.settings_dialog import SettingsDialog
from src.ui.widgets.tabs.expert_tab import ExpertTab
from src.ui.widgets.tabs.pdf_output_tab import PDFOutputTab
from src.ui.widgets.tabs.provider_tab import ProviderTab


class RecordingStore:
    def __init__(self, settings):
        self.settings = settings
        self.calls = {}

    def get_settings(self):
        return self.settings

    def get_providers(self):
        return self.settings.providers.providers

    def update_translation_settings(self, **kwargs):
        self.calls["translation"] = kwargs
        return True

    def update_pdf_settings(self, **kwargs):
        self.calls["pdf"] = kwargs
        return True

    def update_rpc_settings(self, **kwargs):
        self.calls["rpc"] = kwargs
        return True

    def update_path_settings(self, **kwargs):
        self.calls["paths"] = kwargs
        return True

    def update_model(self, provider_id, model_id, model):
        self.calls["model"] = (provider_id, model_id, model)
        return True


class SettingsUiRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_automatic_worker_counts_round_trip_as_none(self):
        store = RecordingStore(Settings())
        tab = ExpertTab(store)

        self.assertEqual(tab.pool_max_workers.value(), 0)
        self.assertEqual(tab.term_pool_max_workers.value(), 0)
        tab.save_settings()
        self.assertIsNone(store.calls["translation"]["pool_max_workers"])
        self.assertIsNone(store.calls["translation"]["term_pool_max_workers"])

        tab.pool_max_workers.setValue(1)
        tab.term_pool_max_workers.setValue(1)
        tab.save_settings()
        self.assertEqual(store.calls["translation"]["pool_max_workers"], 1)
        self.assertEqual(store.calls["translation"]["term_pool_max_workers"], 1)
        self.assertEqual(store.calls["pdf"]["formular_font_pattern"], "")
        self.assertEqual(store.calls["rpc"]["doclayout_host"], "")
        self.assertEqual(store.calls["paths"]["output_dir"], "")

    def test_provider_editor_preserves_custom_base_url(self):
        model = ModelConfig(
            id="model",
            display_name="Internal",
            model_name="internal-model",
            api_key="key",
            base_url="https://gateway.invalid/v1",
        )
        provider = Provider(
            id="openai",
            name="OpenAI",
            default_base_url="https://api.openai.com/v1",
            models=[model],
        )
        settings = Settings()
        settings.providers.providers = [provider]
        store = RecordingStore(settings)
        tab = ProviderTab(store)
        tab.current_provider = provider
        tab.provider_list.setCurrentRow(1)
        tab._update_model_options()
        tab._load_model_config(model)

        self.assertFalse(tab.base_url_input.isReadOnly())
        self.assertEqual(tab.base_url_input.text(), "https://gateway.invalid/v1")
        tab.base_url_input.setText("https://gateway-2.invalid/v1")
        with (
            mock.patch.object(tab, "load_providers"),
            mock.patch("src.ui.widgets.tabs.provider_tab.QMessageBox.information"),
        ):
            tab._on_save_model()

        saved = store.calls["model"][2]
        self.assertEqual(saved.base_url, "https://gateway-2.invalid/v1")

    def test_pdf_tab_never_allows_zero_output_modes(self):
        tab = PDFOutputTab(RecordingStore(Settings()))
        tab.output_dual.setChecked(False)
        tab.output_mono.setChecked(False)
        self.assertTrue(tab.output_dual.isChecked() or tab.output_mono.isChecked())

    def test_settings_dialog_discards_draft_on_cancel_and_commits_once(self):
        committed_service = SettingsService(Settings())
        committed_store = SettingsStore(committed_service)
        with (
            mock.patch(
                "src.ui.widgets.settings_dialog.get_settings_store",
                return_value=committed_store,
            ),
            mock.patch("src.services.settings_service.save_settings") as save,
        ):
            dialog = SettingsDialog()

            dialog.translation_tab.qps_spin.setValue(9)
            dialog.save_settings()
            dialog.reject()
            self.assertEqual(committed_store.get_settings().translation.qps, 4)
            save.assert_not_called()

            dialog.load_settings()
            dialog.translation_tab.qps_spin.setValue(11)
            self.assertTrue(dialog._on_apply())
            save.assert_called_once()

        self.assertEqual(committed_store.get_settings().translation.qps, 11)
        self.assertIsNot(
            committed_store.get_settings(), dialog.settings_store.get_settings()
        )

    def test_settings_dialog_uses_grouped_navigation_and_progressive_term_panel(self):
        committed_store = SettingsStore(SettingsService(Settings(), persist=False))
        with mock.patch(
            "src.ui.widgets.settings_dialog.get_settings_store",
            return_value=committed_store,
        ):
            dialog = SettingsDialog()

        self.assertEqual(dialog.navigation_list.count(), 5)
        self.assertEqual(dialog.stack.count(), 5)
        dialog.navigation_list.setCurrentRow(1)
        self.assertIs(dialog.stack.currentWidget(), dialog.translation_tab)
        dialog.show()
        self.app.processEvents()
        self.assertFalse(dialog.translation_tab.term_settings_frame.isVisible())
        dialog.translation_tab.use_separate_term_model.setChecked(True)
        self.app.processEvents()
        self.assertTrue(dialog.translation_tab.term_settings_frame.isVisible())
        dialog.close()

    def test_main_sidebar_keeps_qps_in_settings_and_maps_task_overrides(self):
        settings = create_default_settings()
        settings.translation.qps = 17
        model = ModelConfig(
            id="model",
            display_name="Model",
            model_name="model",
            api_key="key",
        )
        settings.providers.providers[0].models.append(model)
        settings.providers.selected_model_id = model.id
        store = SettingsStore(SettingsService(settings, persist=False))

        with mock.patch(
            "src.ui.widgets.app_sidebar.get_settings_store", return_value=store
        ):
            sidebar = AppSidebar()

        sidebar.resize(500, 560)
        sidebar.show()
        self.app.processEvents()
        pages_y = sidebar.pages_input.mapTo(
            sidebar, sidebar.pages_input.rect().topLeft()
        ).y()
        output_y = sidebar.output_mode_combo.mapTo(
            sidebar, sidebar.output_mode_combo.rect().topLeft()
        ).y()
        self.assertEqual(pages_y, output_y)

        self.assertFalse(hasattr(sidebar, "qps_spin"))
        sidebar.output_mode_combo.setCurrentIndex(
            sidebar.output_mode_combo.findData("dual")
        )
        sidebar.bilingual_layout_combo.setCurrentIndex(
            sidebar.bilingual_layout_combo.findData("translated_first")
        )
        sidebar.auto_glossary_check.setChecked(False)
        sidebar.glossary_input.setText("/tmp/task.csv")
        config = sidebar.get_config()
        self.assertEqual(config.qps, 17)
        self.assertTrue(config.output_dual)
        self.assertFalse(config.output_mono)
        self.assertTrue(config.use_alternating_pages_dual)
        self.assertTrue(config.dual_translate_first)
        self.assertFalse(config.auto_extract_glossary)
        self.assertEqual(config.glossary_files, "/tmp/task.csv")
        sidebar.close()

    def test_file_queue_is_hidden_until_files_exist_and_has_visible_remove_action(self):
        class FakeTranslationStore(QObject):
            uploaded_files_changed = Signal()

            def __init__(self):
                super().__init__()
                self.uploaded_files = []

            def remove_uploaded_file(self, file_id):
                self.uploaded_files = [
                    file for file in self.uploaded_files if file.id != file_id
                ]
                self.uploaded_files_changed.emit()

        store = FakeTranslationStore()
        with mock.patch(
            "src.ui.widgets.file_uploader.get_translation_store",
            return_value=store,
        ):
            uploader = FileUploader()

        self.assertFalse(uploader.file_list.isVisible())
        store.uploaded_files.append(
            UploadedFile(id="file", name="paper.pdf", path="/tmp/paper.pdf", size=1024)
        )
        store.uploaded_files_changed.emit()
        uploader.show()
        self.app.processEvents()
        self.assertTrue(uploader.file_list.isVisible())
        item_widget = uploader.file_list.itemWidget(uploader.file_list.item(0))
        remove_button = item_widget.findChild(
            type(uploader.browse_button), "file_remove_button"
        )
        self.assertIsNotNone(remove_button)
        remove_button.click()
        self.assertFalse(uploader.file_list.isVisible())
        uploader.close()


if __name__ == "__main__":
    unittest.main()
