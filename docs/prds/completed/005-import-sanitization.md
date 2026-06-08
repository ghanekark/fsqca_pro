# PRD 005: Import Sanitization & Transparency Reporting

## 1. Objective and Scope
### Objective
To enhance the data ingestion process with automated sanitization (renaming, handling missing values) while providing a detailed "Sanitization Report" to the user. This ensures the researcher is fully aware of every change made to their raw data and the rationale behind it (e.g., "spaces replaced with underscores for Boolean engine compatibility").

### Scope
- **In-Scope:** 
    - Automated cleaning of column names (alphanumeric enforcement).
    - Detection and reporting of missing values (blanks vs. placeholder codes).
    - A new "Sanitization Report" dialog displayed after file load.
- **Out-of-Scope:**
    - Manual editing of data within the sanitization report.

---

## 2. Technical Implementation Strategy

### Architecture Layering (MVC/MVVM)
- **Model (`models/data_model.py`):**
    - Enhance the `load_file` method to track each action taken (e.g., `self.sanitization_log.append("Renamed 'Gross GDP' to 'Gross_GDP'")`).
    - Standardize blank values to `NaN` and report the count of dropped rows.
- **View (`views/sanitization_report_dialog.py`):**
    - A simple `QDialog` with a read-only `QTextEdit` or list view displaying the log.
- **Controller (`controllers/analysis_controller.py`):**
    - Intercepts the completion of a file load and triggers the report dialog if any changes were made.

### Implementation Detail
- **Transparency:** Every modification must include a "Reason" (e.g., "fsQCA conventions require alphanumeric variable names").
- **Non-blocking:** The report should appear as a post-load confirmation, ensuring the user is informed before proceeding with analysis.

---

## 3. Development Plan

### Phase 1: Logic Enhancement
1. Update `load_file` in `QCADataModel` to populate a log of changes.
2. Refine the alphanumeric regex for column names to ensure strict Boolean compatibility.

### Phase 2: View Construction
1. Create `views/sanitization_report_dialog.py`.
2. Implement a layout that clearly distinguishes between "Action Taken" and "Reasoning".

### Phase 3: Validation
1. Test with "dirty" datasets (spaces, special characters, mixed missing value codes) to ensure the report is comprehensive and accurate.
