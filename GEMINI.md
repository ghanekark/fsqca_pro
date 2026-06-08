# fsqca_pro: Gemini CLI Development Instructions

These instructions define the operational contract for Gemini CLI when working on the `fsqca_pro` repository. Follow them exactly.

## 1. Project Profile

- **Language:** Python 3.10+
- **Architecture:** Professional `src/` Layout (Clean-Source Layout)
- **UI Stack:** PyQt6 `QtWidgets` only (`QMainWindow`, `QDialog`, `QPushButton`, `QTableWidget`, etc.)
- **Theming:** Centralized Qt Style Sheets (QSS) via `src/styles/template.qss`
- **Target Platforms:** Windows first (Microsoft Store submission ready); preserve macOS compatibility
- **Primary Entry Point:** `src/main.py`

Do not introduce QtQuick / QML, hybrid UI stacks, or platform-specific GUI assumptions.

---

## 2. Directory Structure & Workspace Management

### 2.1 The `src/` Directory
All application logic and source-controlled assets live here.
- `src/main.py`: The main entry point and application controller.
- `src/controllers/`, `src/models/`, `src/views/`, `src/utils/`: Standard MVC components.
- `src/styles/`: Contains `template.qss` and `favicon.ico` (application icon).

### 2.2 The `packaging/` Directory
Contains all build-specific configurations.
- `packaging/fsQCA_pro.iss`: Inno Setup script for Windows installer.
- `packaging/fsQCA_pro.spec`: PyInstaller spec file for bundling the application.
- `packaging/installer_icon.ico`: Icon specifically for the generated setup/exe.

### 2.3 Transient Directories (Ignored)
These folders are generated during the build process and should never be committed or analyzed as source.
- `dist/`: Raw executable output.
- `build/`: Temporary build files.
- `Output/`: Final installers and MSIX packages for the Microsoft Store.
- `_deleted/`: Archive of old/removed files.

---

## 3. Engineering Best Practices for Gemini CLI

### 3.1 Context Efficiency
- **Search Scope:** Always prioritize searching within the `src/` directory for code changes.
- **Ignore Files:** Respect `.geminiignore`. Large scripts like `release.ps1` are ignored by default to save context. Read them explicitly if they need modification.
- **Asset Loading:** Always use the `get_resource_path()` helper in `src/main.py` when adding new assets to ensure they work in both development and frozen (EXE) modes.

### 3.2 Scope Control
- Make the smallest safe edit that satisfies the request.
- Do not refactor unrelated code or perform opportunistic cleanup.
- Preserve public APIs and signal signatures.

### 3.3 Type Safety & Python Style
- Follow PEP 8 rigorously.
- Use explicit type hints on all new functions and methods.
- Prefer readable, explicit code over "clever" abstractions.

---

## 4. Architecture & UI Rules

### 4.1 MVC Boundaries
- Keep domain logic in `src/models/`.
- Keep presentation logic in `src/views/`.
- Use `src/controllers/` for coordination.
- **Signal/Slot Communication:** Always use Qt signals for cross-component events. Do not let views reach directly into models.

### 4.2 Non-Blocking UI
- Never run heavy computation or I/O on the GUI thread.
- Use the worker pattern in `src/utils/worker.py` for background tasks.
- Surface results and errors back to the GUI thread via signals.

### 4.3 Styling & Assets
- **Centralized QSS:** All styling must flow through `src/styles/template.qss`. No inline `setStyleSheet()` calls.
- **Icons:** Use `src/styles/favicon.ico` for the application window. Ensure paths are resolved via `get_resource_path()`.

---

## 5. Packaging & Automation

### 5.1 The `release.ps1` Script
- This script is the "one-click" automation for building and hosting the app.
- It handles cleanup, PyInstaller building, Inno Setup compilation, and GitHub/GitHub Pages hosting.
- **Version Handling:** It manages both `vX.Y.Z` tags and numeric `X.Y.Z` metadata for Windows.

### 5.2 Build Artifacts
- Treat `dist/`, `build/`, and `Output/` as disposable.
- Always use relative paths in `.iss` and `.spec` files (e.g., `../src/...`) to support the project hierarchy.

---

## 6. Testing & Validation

- Use `pytest` for unit tests and `pytest-qt` for widget tests.
- Add regression tests when fixing bugs.
- **Validation is Mandatory:** Never assume a change works without verification. Run the app or the relevant tests before finishing a task.
