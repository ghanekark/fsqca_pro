# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Structured Export Engine (CSV & TXT)**: New export functionality for Truth Tables and Standard Analysis results with dual-format support (TXT/CSV). Outputs are now professionally aligned with Ragin's fsQCA standards, including metadata cutoffs, model definitions, and canonical solution sequencing (Complex → Parsimonious → Intermediate) [PRD 011].
- **Dynamic Theme Engine**: Centralized dark/light mode toggle with persistence across sessions via `QSettings` [PRD 001].
- **Direct Method Calibration Interface**: A specialized interactive dialog for setting qualitative anchors (Full, Crossover, Non-membership) with real-time `matplotlib` histogram visualization [PRD 002].
- **Complexity-Parsimony Continuum Visualizer**: A dedicated tabular view to audit the simplifying assumptions by aligning Complex, Intermediate, and Parsimonious solutions side-by-side [PRD 003].
- **Calibration Metadata Persistence**: Automated tracking and persistence of theoretical justifications and anchors via companion `.meta.json` files [PRD 004].
- **Ingestion Transparency Report**: Automatic generation of a "Sanitization Report" after data load to document all automated cleaning actions (renaming, type conversion, row dropping) [PRD 005].
- **Advanced Necessity Metrics**: Implementation of "Relevance of Necessity" (RoN) and "Triviality" proxies to evaluate the substantive importance of necessary conditions [PRD 006].
- **Batch Auto-Calibration**: Restoration of the single-click utility to calibrate all numeric variables using standard 95th/50th/5th percentile benchmarks [PRD 007].
- **Informed Dichotomization Wizard**: A new guided workflow for converting continuous variables to crisp sets, featuring statistical guidance (mean/median) and theoretical justification fields [PRD 008].
- **Research Transparency & Replicability Logger**: Automated logging of all analytical decisions (recoding, calibration, threshold choices) into a centralized, exportable Markdown/JSON audit trail [PRD 009].
- **Set Coincidence Diagnostic Engine**: Implementation of the coincidence formula to quantify set overlap and alignment, supporting set negation and high-performance vectorized operations [PRD 010].
- **Metadata Tooltips**: Enhanced the main data grid to display calibration anchors and rationales when hovering over column headers.

### Changed
- **UI Uniformity & Semantic Styling**: System-wide refactor to eliminate hardcoded styles. Migrated all visual logic to a centralized semantic system in `template.qss` using Qt Object Names (e.g., `PrimaryButton`, `SuccessButton`, `LinkButton`), ensuring perfect theme responsiveness and design consistency across all dialogs [PRD 012].
- **System-Wide Numeric Filtering**: Systematically updated all analytical modules (Truth Table, Necessity, Subset, Coincidence, Descriptives) to filter for numeric-only variables, preventing mathematical errors on ID or string columns.
- **Theme-Aware UI Palette**: Migrated hardcoded colors in multiple dialogs (Analysis Results, Calibration, Necessity, Sanitization) to use the `palette()` function, ensuring full compatibility with dark mode switching.
- **Asynchronous Workflows**: Refactored Necessity Analysis and Batch Calibration to run in background `QThread` workers, ensuring the UI remains non-blocking for large datasets.

### Fixed
- **AttributeError in DichotomizationWizard**: Corrected `QFrame` enum access to use `QFrame.Shape.StyledPanel`, resolving a crash on launch in PyQt6.
- **NameError in MainWindow**: Resolved missing `pandas` and `numpy` imports in `views/main_window.py` required for type hints.
- **NameError in AppController**: Resolved missing `typing` library imports in `main.py` which prevented application launch after PRD implementations.
