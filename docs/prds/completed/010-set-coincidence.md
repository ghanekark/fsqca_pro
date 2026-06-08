# PRD 010: Set Coincidence Diagnostic Engine

## 1. Objective and Scope
### Objective
To implement the computational logic and result display for the "Set Coincidence" measure. This allows researchers to quantify the degree of overlap and alignment between two fuzzy sets, distinguishing coincidence from simple correlation.

### Scope
- **In-Scope:**
    - Implementation of the coincidence formula: $\frac{\sum \min(X_i, Y_i)}{\sum \max(X_i, Y_i)}$.
    - Enhancing the existing `CoincidenceDialog` to display calculated results.
    - Support for set negation (~X) in the calculation.
    - Integration with the `data_model` for efficient set operations.
- **Out-of-Scope:**
    - Visualizing coincidence via Venn diagrams (reserved for a separate visualization PRD).
    - Multi-set coincidence (beyond pairwise comparison).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py` or new `models/analytical_engine.py`):**
    - Implement `calculate_coincidence(set_x_data, set_y_data)` using NumPy for performance.
- **View (`views/coincidence_dialog.py`):**
    - Update the existing UI to include a "Result" section (labels for the coincidence score).
    - Add a "Calculate" button that triggers the computation.
- **Controller:**
    - Handle the interaction between the dialog and the data model.

### Implementation Detail
- **Formula Accuracy:** Ensure the formula correctly handles both crisp and fuzzy membership scores.
- **Performance:** Use vectorized operations (NumPy) to handle large datasets efficiently.
- **Negation Logic:** Correcty apply $1 - X$ when the "Negate" checkbox is checked.

---

## 3. Development Plan

### Phase 1: Computational Logic
1. Implement the coincidence formula in the backend.
2. Write unit tests to verify the calculation against known benchmarks.

### Phase 2: UI Enhancement
1. Update `CoincidenceDialog` to show results.
2. Connect the "Calculate" button to the backend logic.

### Phase 3: Integration & Validation
1. Verify the tool works with various variable combinations (Negated vs. Non-negated).
2. Ensure the results are clearly communicated to the user (e.g., 3 decimal places).
