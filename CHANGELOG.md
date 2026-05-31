# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Dynamic Theme Engine**: Centralized dark/light mode toggle with persistence across sessions via `QSettings` [PRD 001].
- **Direct Method Calibration Interface**: A specialized interactive dialog for setting qualitative anchors (Full, Crossover, Non-membership) with real-time `matplotlib` histogram visualization [PRD 002].
- **Complexity-Parsimony Continuum Visualizer**: A dedicated tabular view to audit the simplifying assumptions by aligning Complex, Intermediate, and Parsimonious solutions side-by-side [PRD 003].
- **Calibration Metadata Persistence**: Automated tracking and persistence of theoretical justifications and anchors via companion `.meta.json` files [PRD 004].
- **Ingestion Transparency Report**: Automatic generation of a "Sanitization Report" after data load to document all automated cleaning actions (renaming, type conversion, row dropping) [PRD 005].
- **Advanced Necessity Metrics**: Implementation of "Relevance of Necessity" (RoN) and "Triviality" proxies to evaluate the substantive importance of necessary conditions [PRD 006].
- **Batch Auto-Calibration**: Restoration of the single-click utility to calibrate all numeric variables using standard 95th/50th/5th percentile benchmarks [PRD 007].
- **Metadata Tooltips**: Enhanced the main data grid to display calibration anchors and rationales when hovering over column headers.

### Changed
- **Asynchronous Workflows**: Refactored Necessity Analysis and Batch Calibration to run in background `QThread` workers, ensuring the UI remains non-blocking for large datasets.
- **Architectural Refinement**: Applied strict type hinting (PEP 484) and Google-style docstrings across all new and modified modules to meet `GEMINI.md` mandates.
- **Data Model Expansion**: Updated `QCADataModel` to handle complex metadata dictionaries and multi-stage sanitization logic.
- **UI Standardization**: Professional formatting of numeric values in the main data grid (fixed to 4 decimal places).

### Fixed
- **NameError in MainWindow**: Resolved missing `pandas` and `numpy` imports in `views/main_window.py` required for type hints.
- **NameError in AppController**: Resolved missing `typing` library imports in `main.py` which prevented application launch after PRD implementations.
