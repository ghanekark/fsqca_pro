# fsqca_pro: Gemini CLI Development Instructions

These instructions define the operational contract for Gemini CLI when working on the `fsqca_pro` repository. Follow them exactly.

## 1. Project Profile

- **Language:** Python 3.10+
- **UI Stack:** PyQt6 `QtWidgets` only (`QMainWindow`, `QDialog`, `QPushButton`, `QTableWidget`, etc.)
- **Theming:** Centralized Qt Style Sheets (QSS) via `styles/template.qss`
- **Target Platforms:** Windows first; preserve macOS compatibility
- **Architecture:** MVC with a strong controller layer
- **Primary entry point:** `main.py`

Do not introduce QtQuick / QML, hybrid UI stacks, or platform-specific GUI assumptions.

---

## 2. Core Engineering Rules

### 2.1 Scope Control
- Make the smallest change that satisfies the request.
- Do not refactor unrelated code.
- Do not rename symbols, files, modules, or signals unless explicitly requested.
- Do not perform opportunistic cleanup.
- Preserve public APIs, signal signatures, and existing user-visible behavior unless the task requires a change.

### 2.2 Type Safety
- Use explicit type hints on all new functions, methods, and signal-related helpers.
- Avoid `Any` unless required by PyQt or a third-party API boundary.
- Prefer `Protocol`, `TypedDict`, `Enum`, `Literal`, `dataclass`, and concrete container types when they improve clarity.

### 2.3 Python Style
- Follow PEP 8.
- Prefer readable, explicit code over clever code.
- Keep functions short and single-purpose.
- Do not introduce new architectural abstractions unless they reduce complexity immediately.

---

## 3. Architecture Rules

### 3.1 MVC Boundaries
- `models/` contains domain logic, data processing, and state.
- `views/` contains Qt widgets, dialogs, and presentation logic only.
- `controllers/` contains coordination logic between models and views.
- `utils/` contains helpers, workers, formatting, and logging utilities.
- `styles/` contains QSS only.

### 3.2 Controller Discipline
- `main.py` may initialize the application and wire the top-level controller, but it must not accumulate unrelated feature logic.
- Prefer not to expand `AppController` with new, unrelated workflows when a feature-specific controller or helper is the clearer boundary.
- Prefer feature-local orchestration over a monolithic controller when adding new functionality.
- Preserve the current controller/view/model event flow unless a change explicitly requires reworking it.

### 3.3 Signal/Slot Communication
- Use Qt signals and slots for cross-component communication.
- Do not call deep view methods from models.
- Do not let views reach into models for business logic.
- Avoid direct UI updates from worker objects; emit data back to the GUI thread instead.

---

## 4. Threading and Responsiveness

### 4.1 Non-Blocking UI
- Never run file I/O, parsing, export/import, data transformation, or heavy computation on the GUI thread when the task may take more than a trivial amount of time.
- Preserve the application’s responsiveness at all times.

### 4.2 Worker Pattern
- Use the existing worker architecture in `utils/worker.py` as the default threading pattern.
- Consider `QThreadPool` / `QRunnable` when it clearly simplifies a short-lived or isolated task, but keep any change contained and consistent with the existing worker architecture.
- Never update Qt widgets from any background thread.
- Use signals to return results, errors, and completion events to the GUI thread.

### 4.3 Thread-Safety
- Preserve any existing interruption, pause, or tie-breaker behavior in workers.
- Do not bypass or simplify worker synchronization without checking the full call chain.
- Handle worker errors explicitly and surface them back to the controller or view in a controlled way.

---

## 5. Data and Model Rules

### 5.1 Model Responsibilities
- `QCADataModel` owns the application’s Pandas/Numpy data state and transformation logic.
- Keep business rules in the model, not in views.
- Prefer vectorized Pandas/Numpy operations over row-by-row Python loops where practical.

### 5.2 Data Loading and Export
- Keep file loading, parsing, and export logic isolated from UI code.
- Use clear boundaries between:
  - user interaction
  - model transformation
  - result formatting
  - file system access

### 5.3 Structured Data
- Use dataclasses for structured application data where appropriate.
- Do not replace structured model objects with ad hoc dictionaries unless there is a concrete boundary reason.

---

## 6. Table and Grid UI Rules

### 6.1 Current Baseline
- The codebase currently uses `QTableWidget` extensively.
- Preserve existing behavior unless the task specifically targets data-grid performance or refactoring.

### 6.2 New Grid Work
- For any new non-trivial or scalable dataset presentation, prefer `QTableView` with `QAbstractTableModel` or `QAbstractItemModel`.
- Do not add new large item-based tables if a model/view implementation is feasible.
- Avoid cell-by-cell population loops in the GUI thread for large datasets.

### 6.3 Performance Boundary
- Treat any table population that iterates through large Pandas DataFrames as a potential UI freeze risk.
- Move data preparation out of widget code whenever possible.

---

## 7. Styling and Theming Rules

### 7.1 Centralized QSS
- All application styling must flow through `styles/template.qss` and the existing theme controller mechanism.
- Do not introduce scattered `setStyleSheet()` calls in views.
- Do not inline colors, fonts, borders, or theme tokens inside widget code unless there is a narrowly scoped exception.

### 7.2 Styling Mechanism
- Use `objectName` and Qt selectors for styling.
- Preserve the existing `ThemeController` / `ThemeModel` pattern.
- When adding new visual states, extend the centralized QSS instead of duplicating style logic in code.

### 7.3 Theme Changes
- Keep theme generation deterministic and reversible.
- Do not break existing selector names or theme token substitution without a strong reason.

---

## 8. Resources and Assets

- This project is currently text-and-layout driven.
- Do not assume icons, images, or `.qrc` resources exist.
- Do not add absolute filesystem paths for resources.
- Use `pathlib` for paths and keep code compatible with Windows and future macOS builds.
- If assets are introduced later, prefer a Qt resource approach or a clearly defined asset path strategy.

---

## 9. Error Handling and Logging

### 9.1 Logging
- Use the `logging` module.
- Do not use `print()` for normal application flow.
- Use `logger.debug()`, `logger.info()`, `logger.warning()`, `logger.error()`, and `logger.exception()` appropriately.

### 9.2 User-Facing Errors
- Use `QMessageBox.critical()` for fatal or blocking errors.
- Use `QMessageBox.warning()` for validation and recoverable issues.
- Use `QMessageBox.information()` for important user confirmations or state changes.
- Keep user-facing messages concise, accurate, and actionable.

### 9.3 Exception Handling
- Catch exceptions only where you can handle them meaningfully.
- Do not swallow exceptions silently.
- Preserve stack traces in logs for unexpected failures.

---

## 10. Testing Rules

- Require tests for algorithmic changes, bug fixes, and non-trivial business logic changes.
- Use `pytest` for unit tests.
- Use `pytest-qt` for Qt widget and signal/slot tests.
- Add regression tests when fixing bugs.
- Avoid changing behavior without adding or updating tests when practical.
- Keep GUI tests focused on interaction and state, not implementation details.

---

## 11. Packaging and Distribution

- Preserve compatibility with Windows packaging.
- Keep code compatible with PyInstaller builds.
- Avoid runtime assumptions that break frozen executables.
- Do not depend on fragile working-directory behavior.
- Keep file/resource access explicit and portable.

---

## 12. Modification Boundaries

When implementing a change:

1. Read the surrounding code first.
2. Identify the exact affected path through views, controllers, models, and workers.
3. Make the smallest safe edit that satisfies the request.
4. Preserve existing formatting and local conventions.
5. Avoid collateral refactors unless the task explicitly calls for them.
6. Do not introduce new dependencies unless the task explicitly requires them.
7. Do not alter unrelated dialogs, signals, or controllers.

If a request appears to require a broader architectural change, isolate the smallest useful increment first and expand only when needed to complete the requested work cleanly.

---

## 13. Default Implementation Preferences

When multiple valid approaches exist, prefer:
- existing project patterns over new patterns
- explicit code over implicit magic
- controller coordination over view logic
- model-centric data processing over UI-side processing
- centralized QSS over widget-local styling
- small, testable functions over large routines

---

## 14. Deliverable Expectations

For code changes:
- Provide only the requested code or the smallest necessary diff.
- Do not rewrite surrounding modules unless asked.
- Keep behavior consistent unless the user requests a change.
- Preserve the current application architecture unless the task explicitly targets architecture or the requested change depends on a broader adjustment.

For analysis:
- Base conclusions on the repository contents.
- Do not speculate when the codebase provides a clear answer.
