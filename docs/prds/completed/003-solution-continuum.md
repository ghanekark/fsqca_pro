# PRD 003: Complexity-Parsimony Continuum Tabular Visualizer

## 1. Objective and Scope
### Objective
To create a dedicated visualization tool that displays fsQCA results (Complex, Intermediate, and Parsimonious solutions) in a side-by-side tabular format. This allows researchers to easily audit the "Complexity-Parsimony Continuum" and understand which simplifying assumptions were used to reduce configurations.

### Scope
- **In-Scope:** 
    - A new dialog (`SolutionContinuumDialog`) that opens via a dedicated button in the Analysis Results view.
    - A tabular display showing the terms of the three solution types aligned by path.
    - Highlighting of "core" conditions (those that remain in the parsimonious solution).
- **Out-of-Scope:**
    - Editing of solutions within this view.
    - Exporting to LaTeX/Word (to be handled by a separate formatter module).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Stores the results of the "Standard Analysis" (all three solution types).
    - Provides a method to map complex paths to their simplified intermediate and parsimonious counterparts.
- **View (`views/solution_continuum_dialog.py`):**
    - A `QDialog` with a `QTableWidget` or `QTreeView`.
    - Columns: Path Index, Complex Solution, Intermediate Solution, Parsimonious Solution.
- **Controller (`controllers/analysis_controller.py`):**
    - Triggered when the user clicks "View Continuum" in the results window.
    - Passes the solution data from the Model to the View.

### Implementation Detail
- **Side-by-Side Button:** A new button will be added to the existing `AnalysisResultsDialog` to launch this visualizer, ensuring zero disturbance to the standard flow.
- **Visual Encoding:** Use font weight (bold) or icons to distinguish between core and complementary conditions in the intermediate solution.

---

## 3. Development Plan

### Phase 1: View Design
1. Create `views/solution_continuum_dialog.py`.
2. Implement the side-by-side table layout.

### Phase 2: Data Mapping Logic
1. Implement the logic in the Model/Controller to align the terms from different solutions.
2. Ensure that if a term is dropped entirely in the parsimonious solution, the cell reflects this (e.g., "---").

### Phase 3: Integration & Testing
1. Add the "View Continuum" button to the results dialog.
2. Test with standard datasets (like the Inter-war project) to ensure alignment is accurate.
