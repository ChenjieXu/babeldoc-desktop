# Changelog

All notable changes to BabelDOC Desktop are documented here.

## [0.2.0] - 2026-07-17

### Added

- Redesigned translation workspace with task-level language, model, page, output and glossary controls.
- Grouped settings navigation for models, translation quality, PDF output, document processing and advanced options.
- Independent terminology-extraction model configuration.
- Cross-platform GitHub Actions release packaging for macOS, Windows and Linux.
- Versioned release assets, Python wheel and SHA256 checksums.

### Fixed

- Prevented PyInstaller multiprocessing children from creating extra macOS windows and Dock icons.
- Saved results beside the source PDF when no custom output directory is configured.
- Removed the terminal-backed raw macOS executable from release output.
- Corrected page-range and output-mode field alignment.
- Hardened settings migration, atomic writes and packaged resource discovery.

### Changed

- Replaced the previous Tauri/Vue implementation with a native PySide6 application.
- Updated the visual system to a compact desktop control-panel layout.
