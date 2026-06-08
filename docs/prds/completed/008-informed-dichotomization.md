# PRD 008: Informed Dichotomization Wizard

## 1. Objective and Scope
### Objective
To implement a specialized wizard-style interface that guides researchers through the process of converting continuous or fuzzy-set variables into crisp sets (dichotomization). This tool emphasizes "informed" choices by providing statistical guidance and requiring theoretical justification for selected thresholds.

### Scope
- **In-Scope:**
    - A new dialog (`DichotomizationWizard`) with a multi-step or guided layout.
    - Integration with `QCADataModel` to retrieve variable statistics (mean, median, etc.).
    - Interactive threshold selection (manual input or auto-calculation based on mean/median).
    - A mandatory "Theoretical Justification" text field.
    - Generation of a new crisp variable (0/1) in the dataset.
- **Out-of-Scope:**
    - Multi-value QCA (mvQCA) thresholds (handled by separate recode logic).
    - Advanced clustering-based dichotomization (reserved for Phase 2).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Add a method `dichotomize_variable(source_var, threshold, new_name, justification)` to handle the data transformation and log the justification.
- **View (`views/dichotomization_wizard.py`):**
    - A `QDialog` using a `QStackedWidget` or a clear sequential layout.
    - Step 1: Variable selection and distribution overview.
    - Step 2: Threshold setting with "Quick Stats" (Mean, Median, Std Dev).
    - Step 3: Justification entry and final confirmation.
- **Controller (`controllers/analysis_controller.py`):**
    - Logic to bridge the UI inputs to the `data_model`.
    - Ensures the new variable is reflected in the main view.

### Implementation Detail
- **Statistical Guidance:** The UI should display the mean and median of the selected variable to help the user identify a sensible "breaking point."
- **Justification Persistence:** The justification must be passed to the `ResearchLogger` (see PRD 009) to ensure replicability.
- **Validation:** Ensure the threshold is within the actual range of the data.

---

## 3. Development Plan

### Phase 1: View Construction
1. Create `views/dichotomization_wizard.py`.
2. Design the layout with variable selection, statistics display, and justification field.

### Phase 2: Logic & Model Integration
1. Implement the `dichotomize_variable` method in `data_model.py`.
2. Connect UI signals to calculate auto-thresholds (mean/median).

### Phase 3: Validation & Logging
1. Verify the creation of the new column.
2. Ensure the justification is correctly captured in the system logs.
