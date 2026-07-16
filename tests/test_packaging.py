import subprocess
import tomllib
import unittest
from pathlib import Path
from unittest import mock

import build


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PackagingConfigurationTests(unittest.TestCase):
    def test_frozen_entrypoint_dispatches_children_before_gui_imports(self):
        source = (PROJECT_ROOT / "src" / "main.py").read_text(encoding="utf-8")

        freeze_support = source.index("multiprocessing.freeze_support()")
        opencv_initialization = source.index("_fix_opencv_recursion()")
        pyside_import = source.index("from PySide6")
        self.assertLess(freeze_support, opencv_initialization)
        self.assertLess(freeze_support, pyside_import)

    def test_setuptools_discovers_subpackages_and_ships_stylesheets(self):
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as file:
            config = tomllib.load(file)

        setuptools = config["tool"]["setuptools"]
        package_find = setuptools["packages"]["find"]
        self.assertIn("src.*", package_find["include"])
        self.assertTrue(package_find["namespaces"])
        self.assertIn("*.qss", setuptools["package-data"]["src.ui.styles"])

    @mock.patch.object(subprocess, "run")
    @mock.patch.object(build, "get_platform_info", return_value=("linux", "x86_64"))
    def test_nuitka_uses_pyside6_plugin_and_portable_icon_flags(
        self, _platform_info, run
    ):
        build.build_with_nuitka()

        command = run.call_args.args[0]
        self.assertIn("--enable-plugin=pyside6", command)
        self.assertNotIn("--enable-plugin=pyqt6", command)
        self.assertFalse(any(arg.startswith("--windows-icon-") for arg in command))
        self.assertTrue(any("src/ui/styles" in arg for arg in command))
        self.assertIn(str(PROJECT_ROOT / "src" / "main.py"), command)
        run.assert_called_once_with(command, check=True)

    @mock.patch.object(subprocess, "run")
    @mock.patch.object(build, "get_platform_info", return_value=("macos", "arm64"))
    @mock.patch.object(build, "remove_macos_collected_directory")
    @mock.patch.object(build, "update_macos_bundle_metadata")
    @mock.patch("builtins.open")
    def test_pyinstaller_uses_official_cv2_hook_without_rewriting_packages(
        self, file_open, update_metadata, remove_collected, _platform_info, run
    ):
        build.build_with_pyinstaller()

        command = run.call_args.args[0]
        self.assertFalse(any("pyi_rth_cv2.py" in arg for arg in command))
        self.assertFalse((PROJECT_ROOT / "hooks" / "hook-cv2.py").exists())
        self.assertNotIn("--collect-submodules=numpy", command)
        self.assertNotIn("--onefile", command)
        self.assertIn("--noconfirm", command)
        self.assertIn("--osx-bundle-identifier=com.babeldoc.desktop", command)
        self.assertIn(str(PROJECT_ROOT / "src" / "main.py"), command)
        self.assertTrue(any(str(PROJECT_ROOT / "resources") in arg for arg in command))
        file_open.assert_not_called()
        run.assert_called_once_with(command, check=True)
        update_metadata.assert_called_once_with(PROJECT_ROOT)
        remove_collected.assert_called_once_with(PROJECT_ROOT)

    @mock.patch.object(subprocess, "run")
    @mock.patch.object(build, "get_platform_info", return_value=("windows", "amd64"))
    def test_windows_build_embeds_release_version_metadata(self, _platform_info, run):
        build.build_with_pyinstaller()

        command = run.call_args.args[0]
        self.assertIn("--onefile", command)
        self.assertIn(
            f"--version-file={PROJECT_ROOT / 'resources' / 'version_info.txt'}",
            command,
        )

    def test_macos_cleanup_keeps_app_and_removes_terminal_backed_directory(self):
        with (
            mock.patch.object(Path, "is_dir", return_value=True),
            mock.patch.object(build.shutil, "rmtree") as rmtree,
        ):
            build.remove_macos_collected_directory(PROJECT_ROOT)

        rmtree.assert_called_once_with(PROJECT_ROOT / "dist" / "BabelDOC")


if __name__ == "__main__":
    unittest.main()
