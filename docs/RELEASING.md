# Release process

## Current release

- Version: `0.2.0`
- Tag: `v0.2.0`
- Workflow: `.github/workflows/release.yml`

## What GitHub Actions builds

| Platform | Runner | Release asset |
| --- | --- | --- |
| macOS Apple Silicon | `macos-15` | `BabelDOC-v0.2.0-macos-arm64.zip` |
| macOS Intel | `macos-15-intel` | `BabelDOC-v0.2.0-macos-x64.zip` |
| Windows x64 | `windows-latest` | `BabelDOC-v0.2.0-windows-x64.zip` |
| Linux x64 | `ubuntu-22.04` | `BabelDOC-v0.2.0-linux-x64.tar.gz` |
| Python | `ubuntu-22.04` | `babeldoc_desktop-0.2.0-*.whl` |

The release also contains `SHA256SUMS.txt` covering every uploaded asset.

## Pre-release checklist

1. Confirm `src/version.py`, `pyproject.toml`, `resources/version_info.txt`,
   `CHANGELOG.md` and this document use the same version.
2. Run locally:

   ```bash
   uv sync --frozen --extra dev
   uv run --frozen ruff check .
   QT_QPA_PLATFORM=offscreen uv run --frozen python -m unittest discover -s tests -p 'test_*.py' -v
   uv build --wheel --out-dir wheelhouse --clear
   uv run --frozen python build.py
   ```

3. Open GitHub Actions and manually run the `Release` workflow. This verifies
   every platform and exposes downloadable workflow artifacts without creating
   a public Release.
4. Download at least the Windows and macOS artifacts and verify their filenames
   and archive contents.

## Publish

The tag must exactly match `v` plus the application version. For this release:

```bash
git tag -a v0.2.0 -m "BabelDOC Desktop v0.2.0"
git push origin v0.2.0
```

The tag run repeats verification, builds all targets, generates checksums and
creates or updates the GitHub Release through the repository-scoped
`GITHUB_TOKEN`.

## Signing status

The workflow currently produces unsigned public binaries. The macOS app is
ad-hoc signed so its bundle is internally consistent, but it is not notarized.
Windows does not include an Authenticode signature. Add certificate-backed
signing before presenting either binary as a trusted-store installer.
