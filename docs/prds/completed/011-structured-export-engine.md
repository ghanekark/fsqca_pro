# PRD 011: Structured Export Engine (CSV & TXT)

## 1. Objective and Scope
### Objective
To enhance the research workflow by allowing users to export truth table outputs and standard analysis results in both neatly structured CSV and plain text formats. This ensures data portability and facilitates further analysis or reporting in external tools.

### Scope
- **In-Scope:**
    - Adding a file type selection (TXT or CSV) to the export/save dialogs in Truth Table and Analysis modules.
    - Implementing a CSV formatter that transforms Truth Table data (configurations, frequencies, consistency, PRI) into a tabular structure.
    - Implementing a CSV formatter for Standard Analysis results (Complex, Parsimonious, and Intermediate solutions), including coverage and consistency metrics.
    - Ensuring the CSV output is "neatly structured" (proper headers, consistent delimiters).
- **Out-of-Scope:**
    - Direct export to `.xlsx` or other proprietary formats.
    - User-configurable CSV delimiters (defaulting to comma).
    - Exporting raw data (this PRD focuses on analytical outputs).

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model/Utility (`utils/formatter.py`):**
    - Extend the existing formatting logic to include CSV generation.
    - Logic should be decoupled from the UI, accepting raw data/results and returning a CSV-formatted string or writing to a file.
- **View (`views/truth_table_dialog.py` & `views/analysis_results_dialog.py`):**
    - Update the "Export" or "Save" button logic to use `QFileDialog.getSaveFileName` with dual filters: `"Text Files (*.txt);;CSV Files (*.csv)"`.
    - Pass the user's choice (format and path) to the controller/model logic.
- **Controller (`controllers/theme_controller.py` or specific logic in `main.py`):**
    - While `theme_controller` handles themes, the analytical flow is often managed by the dialogs directly or a central controller. Ensure the export logic follows the established pattern in the codebase.

### Implementation Detail
- **CSV Formatting:** Use Python's built-in `csv` module to ensure proper escaping and formatting.
- **Truth Table Structure:** Rows should represent rows of the truth table; columns should include the condition combinations, outcome, number of cases, consistency, and PRI.
- **Analysis Structure:** Results should be partitioned by solution type, with columns for the causal configurations and their respective fit metrics.

---

## 3. Development Plan

### Phase 1: Formatter Enhancement
1. Create or update `utils/formatter.py` to include CSV generation functions.
2. Ensure the functions handle the specific data structures used by the Truth Table and Analysis engines.

### Phase 2: Truth Table Export Integration
1. Modify `views/truth_table_dialog.py` to update the save file dialog.
2. Implement the logic to branch between TXT and CSV formatting based on user selection.

### Phase 3: Standard Analysis Export Integration
1. Modify `views/analysis_results_dialog.py` (or the relevant view for analysis output) to support CSV export.
2. Ensure complex/parsimonious/intermediate solutions are correctly serialized into CSV.

### Phase 4: Validation & Quality Assurance
1. Verify that exported CSV files open correctly in Excel/LibreOffice with proper alignment.
2. Verify that existing TXT export functionality remains intact and bug-free.
3. Ensure all new code adheres to PEP 8 and includes type hints as per `GEMINI.md`.
