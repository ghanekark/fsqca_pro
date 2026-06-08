# PRD 004: Calibration Metadata & Audit Log

## 1. Objective and Scope
### Objective
To implement a system for tracking and persisting the theoretical justifications and qualitative anchors used during the calibration process. This ensures transparency and replicability, as required by fsQCA standards, by maintaining an "audit log" of all data transformations.

### Scope
- **In-Scope:** 
    - Modification of `QCADataModel` to store metadata for each calibrated column.
    - Capturing user-provided justifications during the calibration step.
    - Persisting this metadata within the application state (e.g., as a hidden column or a sidecar JSON/SQLite store).
- **Out-of-Scope:**
    - External export of the log (this will be handled by a general report generator in PRD 007).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Add a `self.calibration_metadata` dictionary (e.g., `{ 'col_name': { 'anchors': [...], 'rationale': '...' } }`).
    - Update `calibrate_variable` to accept a `rationale` string.
- **View (`views/calibration_dialog.py`):**
    - Add a `QTextEdit` field for the user to enter their theoretical justification for the selected anchors.
- **Controller (`controllers/analysis_controller.py`):**
    - Passes the rationale from the view to the model during the calibration process.

### Implementation Detail
- **Persistence:** Ensure that when the project is saved (to `.csv` or `.dat`), the metadata is either embedded in the header or saved as a companion file to prevent loss of context.
- **Auditability:** Provide a way to view the rationale for any calibrated variable (e.g., via a tooltip or a "Properties" dialog).

---

## 3. Development Plan

### Phase 1: Model Expansion
1. Update `QCADataModel` to include the metadata storage structure.
2. Modify the `calibrate_variable` signature to include the `rationale` parameter.

### Phase 2: UI Update
1. Add the "Rationale/Justification" text field to the `CalibrationDialog`.
2. Ensure the field is mandatory (or provides a strong prompt) to encourage good practice.

### Phase 3: Integration
1. Verify that the metadata is correctly stored and can be retrieved for reporting purposes.
