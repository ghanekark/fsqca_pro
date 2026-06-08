# PRD 002: Direct Method Calibration Interface

## 1. Objective and Scope
### Objective
To implement a specialized PyQt6 dialog that allows users to perform "Direct Method" calibration of raw variables into fuzzy sets. This interface will provide a user-friendly wrapper for the existing `calibrate_variable` logic in the data model, enabling the manual setting of three qualitative anchors (Full Membership, Crossover, and Full Non-membership).

### Scope
- **In-Scope:** 
    - A new dialog (`CalibrationDialog`) launched from the main window.
    - Input fields for the three qualitative anchors (numerical).
    - Data visualization (histogram or distribution) of the source variable to aid anchor placement.
    - Integration with `QCADataModel.calibrate_variable`.
- **Out-of-Scope:**
    - Indirect calibration methods (regression-based).
    - Multi-target calibration (calibrating one variable into multiple different fuzzy sets simultaneously).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Existing `calibrate_variable` method remains the core logic.
    - Potential update to store calibration history (see PRD 004).
- **View (`views/calibration_dialog.py`):**
    - A `QDialog` containing `QLineEdit` or `QDoubleSpinBox` for anchors.
    - A `QComboBox` to select the source variable.
    - A `QLineEdit` for the name of the new calibrated variable.
    - A placeholder for a `matplotlib` or `QtCharts` distribution plot (optional but recommended).
- **Controller (`controllers/analysis_controller.py` - or existing logic in main_window):**
    - Orchestrates the opening of the dialog.
    - Gathers inputs and calls the Model.
    - Refreshes the main data view upon successful calibration.

### Implementation Detail
- **Anchor Validation:** The view must ensure that the Crossover point is between the Full and Non-membership anchors.
- **Non-blocking Execution:** The calibration calculation, while fast for small datasets, should ideally be treated as a standard operation that emits a success signal to update the UI.

---

## 3. Development Plan

### Phase 1: View Construction
1. Create `views/calibration_dialog.py`.
2. Implement basic layout with inputs for variable selection, new name, and the three anchors.

### Phase 2: Logic Integration
1. Connect the "Calibrate" button to the controller/model.
2. Implement validation logic to ensure anchors are numerically sound.

### Phase 3: Validation
1. Verify that calibrated values are correctly added as a new column in the main dataframe.
2. Ensure the UI remains responsive throughout the process.
