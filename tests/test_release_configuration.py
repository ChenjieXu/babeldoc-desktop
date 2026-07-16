import tomllib
import unittest
from pathlib import Path

from src.version import __version__


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ReleaseConfigurationTests(unittest.TestCase):
    def test_release_version_is_consistent_across_metadata(self):
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as file_handle:
            project_version = tomllib.load(file_handle)["project"]["version"]

        self.assertEqual(project_version, __version__)
        self.assertIn(
            f"FileVersion', '{__version__}",
            (PROJECT_ROOT / "resources" / "version_info.txt").read_text(),
        )
        self.assertIn(
            f"## [{__version__}]",
            (PROJECT_ROOT / "CHANGELOG.md").read_text(),
        )

    def test_release_workflow_builds_all_desktop_targets_and_publishes_assets(self):
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )

        for required in (
            "macos-15",
            "macos-15-intel",
            "windows-latest",
            "ubuntu-22.04",
            "BabelDOC-python-wheel",
            "SHA256SUMS.txt",
            "gh release create",
            "github.ref_type == 'tag'",
            "tag/version mismatch",
        ):
            self.assertIn(required, workflow)

    def test_maintainer_release_steps_stay_out_of_the_readme(self):
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        release_guide = (PROJECT_ROOT / "docs" / "RELEASING.md").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("发布新版本", readme)
        self.assertNotIn("git tag -a", readme)
        self.assertIn("## Publish", release_guide)
        self.assertIn("git tag -a", release_guide)


if __name__ == "__main__":
    unittest.main()
