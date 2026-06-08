# PRD 007: Batch Auto-Calibration Utility

## 1. Objective and Scope
### Objective
To restore the "Auto-Calibrate All" functionality that allows researchers to quickly transform all numeric variables in a dataset into fuzzy-set variables using a standard "passive" calibration approach (95th, 50th, and 5th percentiles as qualitative anchors).

### Scope
- **In-Scope:** 
    - Re-integrating the "Auto-Calibrate All" button into the Calibration UI.
    - Automated detection of numeric columns that haven't been calibrated yet.
    - Application of the fsQCA log-odds transformation using percentile-based benchmarks.
    - A summary report at the end of the batch process.
- **Out-of-Scope:**
    - Customizing the percentile thresholds for the batch process (this remains fixed at the industry-standard 95/50/5).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Leverage the existing `auto_calibrate_all()` and `auto_calculate_thresholds()` methods.
    - Update these methods to also populate `calibration_metadata` with a standard rationale (e.g., "Automated percentile-based calibration").
- **View (`views/calibration_dialog.py`):**
    - Add a distinct "Batch Auto-Calibrate All" button at the bottom of the input panel.
    - Style the button to distinguish it from the manual "Calibrate" action.
- **Controller (`controllers/analysis_controller.py` - main.py):**
    - Connect the new button to the `model.auto_calibrate_all()` method.
    - Trigger a grid refresh and display a success message with the count of calibrated variables.

### Implementation Detail
- **Non-blocking:** For very large datasets, this process should ideally be run in a background thread to prevent UI freezing, though for standard fsQCA N-sizes (10-100 cases), it is nearly instantaneous.
- **Naming Convention:** Maintain the `f_` prefix for all automatically generated fuzzy columns.

---

## 3. Development Plan

### Phase 1: Model Update
1. Ensure `auto_calibrate_all` is fully compatible with the new `calibration_metadata` structure to ensure transparency logs are maintained even for automated steps.

### Phase 2: UI Integration
1. Add the "Auto-Calibrate All" button to the `CalibrationDialog`.
2. Ensure the dialog remains clean and focused on the "Direct Method" while providing this shortcut.

### Phase 3: Validation
1. Test with a dataset containing multiple numeric and non-numeric columns.
2. Verify that all numeric columns (except those already prefixed with `f_`) are correctly calibrated and appear in the main data grid.
