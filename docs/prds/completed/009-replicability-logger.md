# PRD 009: Research Transparency & Replicability Logger

## 1. Objective and Scope
### Objective
To implement an automated logging system that records all critical analytical decisions made by the researcher. This ensures the research process is transparent, formalized, and fully replicable, adhering to Ragin's "Good Practices."

### Scope
- **In-Scope:**
    - A centralized logger utility (`utils/logger.py`).
    - Recording of: Variable creation/recoding, calibration anchors, threshold choices, and minimization settings.
    - Capturing of qualitative justifications provided in wizards (e.g., Dichotomization Wizard).
    - Exporting the log to a human-readable format (Markdown or Text).
- **Out-of-Scope:**
    - Full "Undo/Redo" state management (this is a logger, not an undo stack).
    - Automatic cloud syncing of logs.

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Utility (`utils/logger.py`):**
    - A singleton `ResearchLogger` class.
    - Methods like `log_action(category, description, metadata)` and `export_log(filepath)`.
- **Controller/Model Integration:**
    - Controllers (e.g., `AnalysisController`) will call the logger whenever a state-altering action is confirmed.
    - Models can also trigger logs for internal data transformations (e.g., `calibrate_variable`).
- **View Integration:**
    - A simple "Export Research Log" option in the File menu of the `MainWindow`.

### Implementation Detail
- **Log Format:** Use a structured format (JSON internally, Markdown for export) that includes timestamps and specific action categories (e.g., "CALIBRATION", "DICHOTOMIZATION", "MINIMIZATION").
- **Non-blocking:** Writing to the log should be efficient and not interfere with UI responsiveness.

---

## 3. Development Plan

### Phase 1: Logger Foundation
1. Create `utils/logger.py` with the base `ResearchLogger` class.
2. Implement basic file writing logic (JSON/Markdown).

### Phase 2: Systematic Integration
1. Integrate logging calls into existing calibration and recode logic.
2. Add "Justification" support to catch data from the Dichotomization Wizard.

### Phase 3: Export & UI
1. Add the "Export Log" action to the `MainWindow`.
2. Verify that a sequence of actions results in a coherent, replicable report.
