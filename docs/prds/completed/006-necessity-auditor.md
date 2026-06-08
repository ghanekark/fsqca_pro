# PRD 006: Necessary Condition Relevance & Triviality Auditor

## 1. Objective and Scope
### Objective
To enhance the necessity analysis module by adding calculations for "Relevance of Necessity" (RoN) and Triviality. This provides researchers with essential metrics to determine if a necessary condition is substantively important or merely "trivial" (e.g., a condition that is present in almost all cases regardless of the outcome).

### Scope
- **In-Scope:** 
    - Implementation of RoN formula: `Σ[min(1-X, 1-Y)] / Σ(1-X)` or equivalent set-theoretic measures.
    - Implementation of Triviality checks (high membership across all cases).
    - Updating the necessity results table to include these new metrics.
- **Out-of-Scope:**
    - Fuzzy typology evaluation (to be handled by PRD 008).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Update `calculate_necessity` to include the RoN and Triviality logic.
    - RoN provides a measure of how much of the non-occurrence of the outcome is explained by the non-occurrence of the condition.
- **View (`views/necessity_dialog.py`):**
    - Add new columns to the results `QTableWidget`: "RoN" and "Triviality".
- **Controller (`controllers/analysis_controller.py`):**
    - Manages the execution of the necessity check and the display of the updated results.

### Implementation Detail
- **Metric Interpretation:** High consistency (>= 0.9) with low RoN indicates a potentially trivial necessary condition.
- **Asynchronous Execution:** Ensure these additional calculations are performed within the existing `AnalysisWorker` thread to maintain UI responsiveness.

---

## 3. Development Plan

### Phase 1: Algorithmic Implementation
1. Add the RoN and Triviality formulas to the Model.
2. Validate formulas against Ragin's foundational texts (e.g., *Redesigning Social Inquiry*).

### Phase 2: UI Expansion
1. Update `views/necessity_dialog.py` to display the new columns.
2. Add tooltips explaining the significance of RoN and Triviality to aid the researcher.

### Phase 3: Validation
1. Test with datasets known to have trivial necessary conditions to ensure the auditor flags them correctly.
