# Design

## Source of truth

- Status: Active
- Last refreshed: 2026-07-17
- Primary product surfaces: main translation workspace, settings dialog, progress and result states
- Evidence reviewed:
  - `README.md`
  - `src/models/settings.py`
  - `src/ui/main_window.py`
  - `src/ui/widgets/*.py`
  - `src/ui/widgets/tabs/*.py`
  - `src/ui/styles/modern.qss`
  - Immersive Translate BabelDOC option screenshots supplied by the user
  - CC Switch main-window screenshot and interface guide

## Brand

- Personality: calm, precise, capable, desktop-native, research-friendly
- Trust signals: explicit selected model, clear output choices, visible task state, local configuration ownership
- Avoid: oversized empty panels, decorative gradients, emoji-dependent iconography, dense walls of switches, hidden billing-impacting options

## Product goals

- Goals:
  - Let a returning user configure and start a PDF translation in under one minute.
  - Keep cost/output-affecting task choices visible before translation starts.
  - Keep provider credentials, compatibility and expert tuning out of the daily workflow.
  - Make empty, running, error and completed states understandable without reading logs.
- Non-goals:
  - Reproduce every Immersive Translate control on the home page.
  - Expose BabelDOC internals that the pinned library version does not support.
  - Turn the desktop app into a document reader/editor.
- Success signals:
  - No permanent blank content region in the default state.
  - Home page has no more than seven task-level decisions before the primary action.
  - Advanced settings remain reachable in two clicks or fewer.
  - Screenshots pass the visual-verdict threshold of 90.

## Personas and jobs

- Primary personas:
  - Researchers translating papers while preserving equations and layout.
  - Knowledge workers translating reports, manuals and business PDFs.
  - Power users bringing their own OpenAI-compatible provider.
- User jobs:
  - When I receive a foreign-language PDF, I want to choose the translation model and output shape quickly, so I can obtain a readable result without learning BabelDOC internals.
  - When a document is unusual, I want advanced compatibility and OCR controls, so I can recover without cluttering every normal translation.
- Key contexts of use: repeated desktop use, multi-file batches, paid API calls, long-running translation jobs

## Information architecture

- Primary navigation:
  - Main workspace
  - Settings via the top-right control or `Cmd/Ctrl + ,`
- Core routes/screens:
  - Main workspace: files, high-frequency task settings, action, progress, results
  - Settings / Models: providers, models, API key, Base URL and provider-specific flags
  - Settings / Translation: QPS, minimum text length, term extraction and custom prompt
  - Settings / Output: watermark policy, default PDF outputs and bilingual ordering
  - Settings / Processing: OCR, rich text, cleanup, formula, line and font behavior
  - Settings / Advanced: worker pools, RPC layout service and default paths
- Content hierarchy:
  - Home, always visible: source language, target language, model, page range, output mode, bilingual order, automatic glossary extraction
  - Home, contextual: glossary files, queued files, progress, errors and results
  - Settings: credentials, defaults, compatibility, OCR, fonts, custom prompt, performance, storage and RPC
  - Hidden: unsupported options or implementation details without a stable BabelDOC 0.5.22 contract

## Design principles

- Daily first: optimize for the repeated translate flow, not configuration completeness.
- Progressive disclosure: task decisions on the home page, defaults and recovery controls in settings.
- State before decoration: use cards, badges and color to communicate state, not to fill space.
- One visual grammar: consistent labels, 12 px corner radius, 1 px borders, compact controls and one primary accent.
- Tradeoffs: the home page duplicates a small set of persisted defaults as runtime overrides to keep the final task contract visible.

## Visual language

- Color:
  - Canvas `#F6F7FB`
  - Surface `#FFFFFF`
  - Primary text `#16181D`
  - Secondary text `#6E7380`
  - Border `#E3E6EC`
  - Primary blue `#1677FF`
  - Action orange `#FF7A1A`
  - Success green `#16A36A`
  - Error red `#E5484D`
- Typography: PingFang SC / SF Pro / Segoe UI fallback; 24 px page title, 16 px card title, 13-14 px controls
- Spacing/layout rhythm: 8 px base grid; 24 px page gutter; 16-20 px card padding; 12-16 px field gaps
- Shape/radius/elevation: 12-14 px cards, 9-10 px inputs, restrained shadow only for primary cards
- Motion: no decorative motion; immediate state changes; progress animation delegated to native Qt
- Imagery/iconography: simple text or vector-like symbols; avoid emoji whose rendering changes by platform

## Components

- Existing components to reuse: `AppHeader`, `FileUploader`, `AppSidebar`, `ActionButtons`, `ProgressDisplay`, `ResultsDisplay`, settings tabs and stores
- New/changed components:
  - Header with product descriptor and compact settings button
  - Workspace intro and compact empty-state card
  - Two-column quick-settings grid
  - Output-mode and bilingual-order selectors
  - Integrated primary action footer
  - Settings left navigation with stacked content pages
- Variants and states: empty, files queued, ready, running, cancelling, error, completed, disabled/no model
- Token/component ownership: global tokens and widget states live in `src/ui/styles/modern.qss`; widgets own structure and content only

## Accessibility

- Target standard: WCAG 2.1 AA where Qt styling permits
- Keyboard/focus behavior: logical tab order, visible focus border, `Cmd/Ctrl + ,` opens settings, Escape closes dialogs
- Contrast/readability: body text and interactive controls must meet 4.5:1 where practical
- Screen-reader semantics: descriptive widget text and tooltips for icon-only buttons
- Reduced motion and sensory considerations: no flashing; color is never the only status indicator

## Responsive behavior

- Supported breakpoints/devices: desktop windows from 1000×680 upward; preferred 1280×800 and above
- Layout adaptations: right configuration column remains readable at minimum width; scroll content rather than compress controls below usable size
- Touch/hover differences: hover is enhancement only; every action remains visible or keyboard reachable

## Interaction states

- Loading: progress card shows stage, percentage and optional logs
- Empty: upload card carries the main instruction; no empty list container is rendered
- Error: inline error card plus dialog for task-stopping failures
- Success: result cards show file type and reveal/open action
- Disabled: primary action explains missing file/model through nearby readiness copy
- Offline/slow network: running state remains cancellable; logs are secondary detail

## Content voice

- Tone: concise, calm, operational
- Terminology: use “模型”, “双语 PDF”, “单语 PDF”, “页面范围”, “兼容模式” consistently
- Microcopy rules: state consequence before implementation detail; avoid “专家” wording unless the control can break output

## Implementation constraints

- Framework/styling system: PySide6 widgets and QSS; no new dependency or webview layer
- Design-token constraints: reuse object names and QSS selectors before adding inline styles
- Performance constraints: no image-heavy background, animation loop or network request for presentation
- Compatibility constraints: macOS, Windows and Linux; avoid platform-specific emoji/icon assumptions
- Test/screenshot expectations:
  - Offscreen main-window and settings screenshots at 1400×900 and 1000×700
  - Existing unit tests remain green
  - Visual-verdict score must reach 90+
  - Wheel and PyInstaller smoke checks remain green

## Open questions

- [ ] Confirm whether “cswitch” refers to CC Switch; current design assumes it does. Owner: product. Impact: visual reference only.
- [ ] Decide whether glossary files should persist as defaults or remain task-only after the first redesigned release. Owner: product. Impact: request model and settings migration.
- [ ] Consider a future scanned-PDF detection prompt that reveals OCR controls contextually. Owner: product/engineering. Impact: post-MVP workflow.
