import json
import os
import tempfile
import unittest
from unittest import mock

from src.utils import config


class SecureConfigTests(unittest.TestCase):
    def test_settings_are_written_atomically_with_private_permissions(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch.dict(os.environ, {"HOME": home}):
                payload = {"providers": {"providers": [{"apiKey": "secret"}]}}
                config.save_settings(payload)

                settings_path = config.get_settings_path()
                self.assertEqual(json.loads(settings_path.read_text()), payload)

                if os.name == "posix":
                    self.assertEqual(settings_path.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(settings_path.parent.stat().st_mode & 0o777, 0o700)

    def test_failed_replace_preserves_existing_settings(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch.dict(os.environ, {"HOME": home}):
                config.save_settings({"version": "old"})
                settings_path = config.get_settings_path()

                with self.assertLogs("src.utils.config", level="ERROR"):
                    with mock.patch(
                        "src.utils.config.os.replace", side_effect=OSError("blocked")
                    ):
                        with self.assertRaises(OSError):
                            config.save_settings({"version": "new"})

                self.assertEqual(
                    json.loads(settings_path.read_text()), {"version": "old"}
                )
                self.assertEqual(list(settings_path.parent.glob("*.tmp")), [])

    def test_loading_hardens_an_existing_file(self):
        if os.name != "posix":
            self.skipTest("POSIX permission semantics only")

        with tempfile.TemporaryDirectory() as home:
            with mock.patch.dict(os.environ, {"HOME": home}):
                settings_path = config.get_settings_path()
                settings_path.write_text('{"value": 1}', encoding="utf-8")
                settings_path.chmod(0o644)

                self.assertEqual(config.load_settings(), {"value": 1})
                self.assertEqual(settings_path.stat().st_mode & 0o777, 0o600)

    def test_semantically_invalid_settings_recover_usable_fields(self):
        settings = config.dict_to_settings(
            {
                "providers": [],
                "translation": {"qps": "invalid", "langOut": "fr"},
                "pdf": {"outputDual": False, "outputMono": False},
                "paths": "invalid",
            }
        )

        self.assertEqual(settings.translation.qps, 4)
        self.assertEqual(settings.translation.lang_out, "fr")
        self.assertTrue(settings.providers.providers)
        self.assertTrue(settings.pdf.output_dual)
        self.assertFalse(settings.pdf.output_mono)
        self.assertEqual(settings.paths.output_dir, "")

    def test_partial_model_preserves_custom_endpoint(self):
        settings = config.dict_to_settings(
            {
                "providers": {
                    "providers": [
                        {
                            "id": "openai",
                            "models": [
                                {
                                    "id": "internal",
                                    "modelName": "gateway-model",
                                    "baseUrl": "https://gateway.invalid/v1",
                                }
                            ],
                        }
                    ],
                    "selectedModelId": "internal",
                }
            }
        )

        provider = next(p for p in settings.providers.providers if p.id == "openai")
        self.assertEqual(provider.models[0].display_name, "gateway-model")
        self.assertEqual(provider.models[0].api_key, "")
        self.assertEqual(provider.models[0].base_url, "https://gateway.invalid/v1")
        self.assertEqual(settings.providers.selected_model_id, "internal")

    def test_legacy_null_text_fields_migrate_to_empty_strings(self):
        settings = config.dict_to_settings(
            {
                "pdf": {
                    "formularFontPattern": None,
                    "formularCharPattern": None,
                },
                "paths": {
                    "outputDir": None,
                    "workingDir": None,
                    "glossaryFiles": None,
                },
            }
        )

        self.assertEqual(settings.pdf.formular_font_pattern, "")
        self.assertEqual(settings.pdf.formular_char_pattern, "")
        self.assertEqual(settings.paths.output_dir, "")
        self.assertEqual(settings.paths.working_dir, "")
        self.assertEqual(settings.paths.glossary_files, "")


if __name__ == "__main__":
    unittest.main()
