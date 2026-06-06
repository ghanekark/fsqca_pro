import os
import sys
import logging
from typing import List, Dict, Any, Tuple, Optional, Callable
import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog, QProgressDialog, QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QDialogButtonBox
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from views.main_window import MainWindow
from views.analysis_results_dialog import AnalysisResultsDialog
from views.calibration_dialog import CalibrationDialog
from views.dichotomization_wizard import DichotomizationWizard
from views.compute_dialog import ComputeDialog
from views.necessity_dialog import NecessityDialog
from views.truth_table_dialog import VariableSelectionDialog, EditTruthTableDialog, DeleteAndCodeDialog, SpecifyAnalysisDialog, PrimeImplicantChartDialog
from views.assumptions_dialog import AssumptionsDialog
from views.sensitivity_dialog import SensitivityDialog
from views.recode_dialog import RecodeDialog
from views.subset_dialog import SubsetDialog
from views.descriptives_dialog import DescriptivesDialog
from views.coincidence_dialog import CoincidenceDialog
from views.select_if_dialog import SelectIfDialog
from views.sanitization_report_dialog import SanitizationReportDialog
from models.data_model import QCADataModel
from controllers.theme_controller import ThemeController
from utils.worker import AnalysisWorker
from utils.formatter import ResultFormatter
from utils.logger import ResearchLogger

class AppController:
    def __init__(self) -> None:
        # Enable High-DPI scaling before creating QApplication
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        self.app = QApplication(sys.argv)

        self.model = QCADataModel()
        self.theme_controller = ThemeController()
        self.logger = ResearchLogger()

        self.view = MainWindow()
        self.view.setMinimumSize(800, 600)

        # Setup application icon
        if os.path.exists("logo.png"):
            self.app_icon = QIcon("logo.png")
            self.app.setWindowIcon(self.app_icon)
            self.view.setWindowIcon(self.app_icon)
        elif os.path.exists("logo.ico"):
            self.app_icon = QIcon("logo.ico")
            self.app.setWindowIcon(self.app_icon)
            self.view.setWindowIcon(self.app_icon)

        # Apply initial theme
        current_theme = self.theme_controller.get_current_theme()
        self.theme_controller.apply_theme(current_theme)
        self.view.action_view_dark_mode.setChecked(current_theme == "dark")

        self.current_tt_df = None
        self.current_conditions = None
        self.current_outcome = None
        self.tt_edit_dialog = None
        self.analysis_config = None

        self._setup_connections()

    def _setup_connections(self):
        # --- File Menu ---
        self.view.action_file_new.triggered.connect(self.new_file)
        self.view.action_file_new_expr.triggered.connect(self.new_from_expression)
        self.view.action_file_open.triggered.connect(self.open_file)
        self.view.action_file_save.triggered.connect(self.save_file)
        self.view.action_file_save_as.triggered.connect(self.save_file)
        self.view.action_file_print_res.triggered.connect(self.print_results)
        self.view.action_file_save_res.triggered.connect(self.save_results)
        self.view.action_file_export_log.triggered.connect(self.export_research_log)
        self.view.action_file_quit.triggered.connect(self.view.close)

        # --- Variables Menu ---
        self.view.action_vars_add.triggered.connect(self.add_variable)
        self.view.action_vars_delete.triggered.connect(self.delete_variable)
        self.view.action_vars_compute.triggered.connect(self.open_compute_dialog)
        self.view.action_vars_recode.triggered.connect(self.open_recode_dialog)
        self.view.action_vars_dichotomize.triggered.connect(self.open_dichotomization_wizard)
        self.view.action_vars_calibrate.triggered.connect(self.open_calibration_dialog)

        # --- Cases Menu ---
        self.view.action_cases_add.triggered.connect(self.add_case)
        self.view.action_cases_delete.triggered.connect(self.delete_case)
        self.view.action_cases_select_if.triggered.connect(self.open_select_if_dialog)
        self.view.action_cases_cancel_sel.triggered.connect(self.cancel_selection)

        # --- Analyze Menu ---
        self.view.action_analyze_tt.triggered.connect(self.open_truth_table_dialog)
        self.view.action_analyze_induction.triggered.connect(self._not_implemented)
        self.view.action_analyze_necessity.triggered.connect(self.open_necessity_dialog)
        self.view.action_analyze_coincidence.triggered.connect(self.open_coincidence_dialog)
        self.view.action_analyze_subset.triggered.connect(self.open_subset_dialog)
        self.view.action_analyze_sensitivity.triggered.connect(self.open_sensitivity_dialog)
        self.view.action_stats_descriptives.triggered.connect(self.open_descriptives_dialog)

        # --- Graphs Menu ---
        self.view.action_graphs_xy.triggered.connect(self._not_implemented)

        # --- View Menu ---
        self.view.action_view_dark_mode.triggered.connect(self.theme_controller.toggle_theme)

    def _not_implemented(self):
        QMessageBox.information(self.view, "Coming Soon", "This feature is on the roadmap but not yet implemented.")

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

    def new_file(self):
        if self.model.dataframe is not None and not self.model.dataframe.empty:
            reply = QMessageBox.question(
                self.view, 'Confirmation',
                "Discard current dataset and create a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        success, message = self.model.new_dataset()
        if success:
            self._reset_analysis_state()
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            QMessageBox.information(self.view, "Success", message)

    def new_from_expression(self):
        if self.model.dataframe is None:
             # Basic safety
             pass

        if self.model.dataframe is not None and not self.model.dataframe.empty:
            reply = QMessageBox.question(
                self.view, 'Confirmation',
                "Discard current dataset and create a new one?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return

        text, ok = QInputDialog.getText(
            self.view, "New from Expression",
            "Enter variable names (separated by space or comma):"
        )
        if ok and text:
            success, message = self.model.new_from_expression(text)
            if success:
                self._reset_analysis_state()
                self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                QMessageBox.information(self.view, "Success", message)

    def add_variable(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load or create a dataset first.")
            return

        text, ok = QInputDialog.getText(self.view, "Add Variable", "New Variable Name:")
        if ok and text:
            success, message = self.model.add_variable(text)
            if success:
                self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                self.logger.log_action(
                    category="VARIABLE_CREATION",
                    description=f"Manually added a new variable named '{text}'."
                )
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.warning(self.view, "Warning", message)

    def delete_variable(self):
        if self.model.dataframe is None or len(self.model.dataframe.columns) == 0:
            return

        cols = list(self.model.dataframe.columns)
        var_name, ok = QInputDialog.getItem(self.view, "Delete Variable", "Select variable to delete:", cols, 0, False)      

        if ok and var_name:
            reply = QMessageBox.question(
                self.view, 'Confirmation',
                f"Are you sure you want to delete variable '{var_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                if self.model.delete_variable(var_name):
                    self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                    self.logger.log_action(
                        category="VARIABLE_DELETION",
                        description=f"Manually deleted variable '{var_name}'."
                    )
                    self._reset_analysis_state()

    def add_case(self):
        if self.model.dataframe is None:
            # Create a basic dataframe with ID if it doesn't exist
            # But usually we want some columns. Let's just create an empty one with one column 'ID'
            self.model.dataframe = pd.DataFrame(columns=['ID'])

        if self.model.add_case():
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            self.logger.log_action(
                category="CASE_CREATION",
                description="Manually added a new case (row)."
            )
        else:
            QMessageBox.warning(self.view, "Warning", "Cannot add a case to an empty variable set. Please add variables first.")

    def delete_case(self):
        if self.model.dataframe is None or self.model.dataframe.empty:
            return

        row_idx = self.view.table.currentRow()
        if row_idx < 0:
            QMessageBox.warning(self.view, "Warning", "Please select a row to delete.")
            return

        reply = QMessageBox.question(
            self.view, 'Confirmation',
            f"Are you sure you want to delete case {row_idx + 1}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.model.delete_case(row_idx):
                self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                self.logger.log_action(
                    category="CASE_DELETION",
                    description=f"Manually deleted case at row {row_idx + 1}."
                )
                self._reset_analysis_state()

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self.view,
            "Open Data File",
            "",
            "CSV and DAT files (*.csv *.dat);;All files (*.*)"
        )

        if filepath:
            success, message = self.model.load_file(filepath)
            if success:
                self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                self.logger.log_action(
                    category="DATA_INGESTION",
                    description=f"Loaded dataset from {filepath}.",
                    metadata={"path": filepath}
                )
                self._reset_analysis_state()

                # Show Sanitization Report (PRD 005)
                if self.model.sanitization_log:
                    report_dialog = SanitizationReportDialog(self.view, self.model.sanitization_log)
                    report_dialog.exec()
                else:
                    QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)

    def save_file(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "No data to save.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self.view,
            "Save Data File",
            "",
            "CSV files (*.csv);;DAT files (*.dat)"
        )

        if filepath:
            success, message = self.model.save_file(self.model.dataframe, filepath)
            if success:
                self.logger.log_action(
                    category="DATA_EXPORT",
                    description=f"Saved current dataset to {filepath}.",
                    metadata={"path": filepath}
                )
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)

    def save_results(self):
        text = self.view.log_console.toPlainText()
        if not text.strip():
            QMessageBox.warning(self.view, "Warning", "The Results Log is empty.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self.view,
            "Save Results Log",
            "",
            "Text files (*.txt);;All files (*.*)"
        )

        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("-" * 40 + "\n")
                    f.write(" fsqca_pro Analysis Report\n")
                    f.write("-" * 40 + "\n\n")
                    f.write(text)
                QMessageBox.information(self.view, "Success", f"Results successfully saved to {filepath}")
            except Exception as e:
                QMessageBox.critical(self.view, "Error", f"Failed to save results: {str(e)}")

    def print_results(self):
        text = self.view.log_console.toPlainText()
        if not text.strip():
            QMessageBox.warning(self.view, "Warning", "The Results Log is empty.")
            return

        printer = QPrinter()
        dialog = QPrintDialog(printer, self.view)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.view.log_console.print(printer)

    def export_research_log(self):
        """Exports the research log as a human-readable Markdown report."""
        if not self.logger.log_entries:
            QMessageBox.warning(self.view, "Warning", "No actions have been recorded in this session.")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self.view,
            "Export Research Log",
            "",
            "Markdown files (*.md);;Text files (*.txt);;All files (*.*)"
        )

        if filepath:
            if self.logger.export_log(filepath):
                QMessageBox.information(self.view, "Success", f"Research log exported to {filepath}")
            else:
                QMessageBox.critical(self.view, "Error", "Failed to export research log.")

    def _reset_analysis_state(self):

        self.current_tt_df = None
        self.current_conditions = None
        self.current_outcome = None
        self.analysis_config = None

    def open_compute_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        cols = list(self.model.dataframe.columns)
        dialog = ComputeDialog(self.view, cols, self._perform_compute)
        dialog.exec()

    def open_recode_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        dialog = RecodeDialog(self.view, numeric_cols)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            source, target, rules = dialog.get_recode_parameters()
            if not target:
                QMessageBox.warning(self.view, "Warning", "Please specify a target variable name.")
                return

            success, message = self.model.apply_recode(source, target, rules)
            if success:
                self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                self.logger.log_action(
                    category="RECODE",
                    description=f"Recoded variable '{source}' into '{target}'.",
                    metadata={"source": source, "target": target, "rules": rules}
                )
                self._reset_analysis_state()
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)

    def _perform_compute(self, target_col, expression):
        success, message = self.model.compute_variable(target_col, expression)
        if success:
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            self.logger.log_action(
                category="COMPUTE",
                description=f"Computed new variable '{target_col}' using expression: {expression}.",
                metadata={"target": target_col, "expression": expression}
            )
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.critical(self.view, "Error", message)

    def open_calibration_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        # get_data_callback is needed for plotting
        def get_data(col):
            if self.model.dataframe is not None and col in self.model.dataframe.columns:
                return self.model.dataframe[col].values
            return None

        dialog = CalibrationDialog(
            self.view,
            numeric_cols,
            get_data,
            self._perform_calibration,
            self.model.auto_calculate_thresholds,
            self._perform_batch_calibration
        )
        dialog.exec()

    def open_dichotomization_wizard(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only (PRD 008 Update)
        df = self.model.dataframe
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        def get_data(col):
            if self.model.dataframe is not None and col in self.model.dataframe.columns:
                return self.model.dataframe[col].values
            return None

        dialog = DichotomizationWizard(
            self.view,
            numeric_cols,
            get_data,
            self._perform_dichotomization
        )
        dialog.exec()

    def _perform_dichotomization(self, source_col, threshold, new_col, rationale=""):
        success, message = self.model.dichotomize_variable(source_col, threshold, new_col, rationale)
        if success:
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Success", message)
            self.append_to_log("DICHOTOMIZATION", f"Variable: {new_col}\nSource: {source_col}\nThreshold: {threshold}\nRationale: {rationale}")
        else:
            QMessageBox.critical(self.view, "Error", message)

    def _perform_calibration(self, source_col, new_col, p_full, p_cross, p_non, rationale=""):
        success, message = self.model.calibrate_variable(source_col, new_col, p_full, p_cross, p_non)
        # For now, we ignore the rationale or just log it to console
        if success:
            print(f"Calibration Rationale for {new_col}: {rationale}")
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.critical(self.view, "Error", message)

    def _perform_batch_calibration(self) -> None:
        """
        Executes automated calibration for all numeric columns in a background thread.
        Maintains scientific transparency by logging rationales for each variable.
        """
        self.progress_dialog = QProgressDialog("Calibrating all numeric variables...", None, 0, 0, self.view)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        def run_batch_math() -> Tuple[bool, str]:
            return self.model.auto_calibrate_all()

        self.batch_worker = AnalysisWorker(run_batch_math)
        self.batch_worker.finished_signal.connect(self._on_batch_finished)
        self.batch_worker.error_signal.connect(self._on_analysis_error)
        self.batch_worker.start()

    def _on_batch_finished(self, result: Tuple[bool, str]) -> None:
        """Handles the completion of the batch calibration process."""
        self.progress_dialog.close()
        success, message = result
        if success:
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Batch Calibration Complete", message)
        else:
            QMessageBox.critical(self.view, "Error", message)

    def open_truth_table_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        dialog = VariableSelectionDialog(self.view, numeric_cols, self._on_tt_generate)
        dialog.exec()

    def _on_tt_generate(self, conditions, outcome, negate_outcome=False):
        self.current_conditions = conditions
        self.current_outcome = f"~{outcome}" if negate_outcome else outcome

        self.progress_dialog = QProgressDialog("Generating Truth Table...", None, 0, 0, self.view)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        def run_tt_math():
            return self.model.generate_truth_table(conditions, outcome, negate_outcome)

        self.tt_worker = AnalysisWorker(run_tt_math)
        self.tt_worker.finished_signal.connect(self._on_tt_finished)
        self.tt_worker.error_signal.connect(self._on_analysis_error)
        self.tt_worker.start()

    def _on_tt_finished(self, tt_df):
        self.progress_dialog.close()
        self.current_tt_df = tt_df

        if self.current_tt_df is not None:
            self.tt_edit_dialog = EditTruthTableDialog(
                self.view,
                self.current_tt_df,
                self.model,
                self.open_standard_analysis,
                self._on_delete_and_code,
                self.open_specify_analysis
            )
            self.tt_edit_dialog.show()

    def open_specify_analysis(self):
        dialog = SpecifyAnalysisDialog(self.view)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.analysis_config = dialog.get_configuration()
            QMessageBox.information(self.view, "Success", "Analysis configuration updated.")

    def _on_delete_and_code(self):
        dialog = DeleteAndCodeDialog(self.view, self.current_outcome)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            freq_thresh = dialog.get_frequency()
            consist_thresh = dialog.get_consistency()
            if self.model.delete_and_code(freq_thresh, consist_thresh):
                self.current_tt_df = self.model.truth_table_df
                if self.tt_edit_dialog:
                    self.tt_edit_dialog.refresh_grid(self.current_tt_df)

    def open_standard_analysis(self):
        if self.current_tt_df is None:
            QMessageBox.warning(self.view, "Warning", "Please generate a Truth Table first.")
            return

        freq_thresh, ok1 = QInputDialog.getInt(self.view, "Analysis Parameters", "Frequency Threshold:", 1, 0)
        if not ok1: return

        consist_thresh, ok2 = QInputDialog.getDouble(self.view, "Analysis Parameters", "Consistency Threshold:", 0.8, 0.0, 1.0, 2)
        if not ok2: return

        dialog = AssumptionsDialog(
            self.view,
            self.current_conditions,
            lambda assumptions: self._perform_standard_analysis(freq_thresh, consist_thresh, assumptions)
        )
        dialog.exec()

    def _perform_standard_analysis(self, freq_thresh, consist_thresh, assumptions):
        self.progress_dialog = QProgressDialog("Running Quine-McCluskey Minimization...", None, 0, 0, self.view)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        def run_heavy_math():
            results = self.model.run_standard_analysis(
                self.current_tt_df,
                freq_thresh,
                consist_thresh,
                assumptions,
                analysis_config=self.analysis_config,
                tie_breaker_callback=self.worker.handle_tie_break
            )

            # Metadata for formatting
            results['frequency_cutoff'] = freq_thresh
            results['consistency_cutoff'] = consist_thresh
            results['assumptions'] = assumptions

            # Calculate metrics for solutions
            results['complex_metrics'] = self.model.calculate_metrics(
                results['complex'], results['conditions'], self.current_outcome
            )
            results['parsimonious_metrics'] = self.model.calculate_metrics(
                results['parsimonious'], results['conditions'], self.current_outcome
            )
            results['intermediate_metrics'] = self.model.calculate_metrics(
                results['intermediate'], results['conditions'], self.current_outcome
            )
            return results

        self.worker = AnalysisWorker(run_heavy_math)
        self.worker.finished_signal.connect(self._on_analysis_finished)
        self.worker.error_signal.connect(self._on_analysis_error)
        self.worker.tie_break_signal.connect(self._on_tie_break_needed)
        self.worker.start()

    def _on_tie_break_needed(self, tied_pis):
        dialog = PrimeImplicantChartDialog(self.view, tied_pis, self.current_conditions)
        dialog.exec()
        selected = dialog.get_selected()
        self.worker.resolve_tie_break(selected)

    def _on_analysis_finished(self, results):
        self.progress_dialog.close()
        results['outcome_name'] = self.current_outcome
        dialog = AnalysisResultsDialog(self.view, results)
        dialog.exec()

        # 1. Format text report for the log using the dedicated Formatter
        report = ResultFormatter.format_standard_analysis(results, self.current_outcome)
        self.append_to_log("STANDARD QCA MINIMIZATION", report)
        
        # 2. Log action for replicability (PRD 009)
        self.logger.log_action(
            category="MINIMIZATION_RESULT",
            description=f"Standard analysis completed for outcome '{self.current_outcome}'.",
            metadata={
                "outcome": self.current_outcome,
                "complex_solution": results['complex'],
                "intermediate_solution": results['intermediate'],
                "parsimonious_solution": results['parsimonious']
            }
        )

    def _on_analysis_error(self, err):
        self.progress_dialog.close()
        QMessageBox.critical(self.view, "Analysis Error", err)
        self.append_to_log("ANALYSIS ERROR", str(err))

    def append_to_log(self, title, text_content):
        """Appends formatted content to the monospace Results Log."""
        header = f"\n{'='*20} {title} {'='*20}\n"
        self.view.log_console.append(header)
        self.view.log_console.append(text_content)
        # Auto-scroll to bottom
        self.view.log_console.verticalScrollBar().setValue(
            self.view.log_console.verticalScrollBar().maximum()
        )

    def open_necessity_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        self.necessity_dialog = NecessityDialog(self.view, numeric_cols)
        self.necessity_dialog.analyze_requested.connect(self._perform_necessity_analysis)
        self.necessity_dialog.show()

    def _perform_necessity_analysis(self, conditions, outcome, negate_outcome):
        self.progress_dialog = QProgressDialog("Analyzing Necessary Conditions...", None, 0, 0, self.view)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        def run_necessity_math():
            return self.model.calculate_necessary_conditions(conditions, outcome, negate_outcome)

        self.necessity_worker = AnalysisWorker(run_necessity_math)
        self.necessity_worker.finished_signal.connect(self._on_necessity_finished)
        self.necessity_worker.error_signal.connect(self._on_analysis_error)
        self.necessity_worker.start()

    def _on_necessity_finished(self, df_results):
        self.progress_dialog.close()
        if df_results is not None:
            # 1. Append to Log
            text_report = ResultFormatter.format_necessity(df_results)
            self.append_to_log("NECESSARY CONDITIONS ANALYSIS", text_report)

            # 2. Update the open dialog
            if hasattr(self, 'necessity_dialog') and self.necessity_dialog.isVisible():
                self.necessity_dialog.display_results(df_results)

    def open_subset_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        dialog = SubsetDialog(self.view, numeric_cols, self._perform_subset_analysis)
        dialog.exec()

    def _perform_subset_analysis(self, conditions, outcome, negate_outcome):
        self.progress_dialog = QProgressDialog("Calculating Subset/Superset Analysis...", None, 0, 0, self.view)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()

        def run_subset_math():
            return self.model.run_subset_superset_analysis(conditions, outcome, negate_outcome)

        self.subset_worker = AnalysisWorker(run_subset_math)
        self.subset_worker.finished_signal.connect(self._on_subset_finished)
        self.subset_worker.error_signal.connect(self._on_analysis_error)
        self.subset_worker.start()

    def _on_subset_finished(self, df_results):
        self.progress_dialog.close()
        if df_results is not None:
            # 1. Append to Log
            text_report = ResultFormatter.format_subset(df_results)
            self.append_to_log("SUBSET ANALYSIS", text_report)

            # 2. Show popup window
            dialog = QDialog(self.view)
            dialog.setWindowTitle("Subset/Superset Analysis Results")
            dialog.resize(900, 500)
            layout = QVBoxLayout(dialog)

            table = QTableWidget()
            table.setColumnCount(len(df_results.columns))
            table.setRowCount(len(df_results))
            table.setHorizontalHeaderLabels(df_results.columns)

            for r_idx, row in enumerate(df_results.itertuples(index=False)):
                for c_idx, val in enumerate(row):
                    if isinstance(val, (int, float, np.float64, np.int64)):
                        item = QTableWidgetItem(f"{val:.4f}")
                    else:
                        item = QTableWidgetItem(str(val))
                    table.setItem(r_idx, c_idx, item)

            table.resizeColumnsToContents()
            layout.addWidget(table)

            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            btn_box.accepted.connect(dialog.accept)
            layout.addWidget(btn_box)

            dialog.exec()

    def open_descriptives_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        dialog = DescriptivesDialog(self.view, numeric_cols)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_vars = dialog.get_selected_variables()
            if not selected_vars:
                return

            # Calculate stats
            stats_df = self.model.dataframe[selected_vars].describe().round(3)
            # Insert 'Statistic' column for readability
            stats_df.insert(0, 'Statistic', stats_df.index)

            # 1. Append to Log
            text_report = ResultFormatter.format_descriptives(stats_df)
            self.append_to_log("DESCRIPTIVE STATISTICS", text_report)

            # 2. Show results in a table dialog
            res_dialog = QDialog(self.view)
            res_dialog.setWindowTitle("Descriptive Statistics")
            res_dialog.resize(800, 400)
            layout = QVBoxLayout(res_dialog)

            table = QTableWidget()
            table.setColumnCount(len(stats_df.columns))
            table.setRowCount(len(stats_df))
            table.setHorizontalHeaderLabels(stats_df.columns)

            for r_idx, row in enumerate(stats_df.itertuples(index=False)):
                for c_idx, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    table.setItem(r_idx, c_idx, item)

            table.resizeColumnsToContents()
            layout.addWidget(table)

            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            btn_box.accepted.connect(res_dialog.accept)
            layout.addWidget(btn_box)

            res_dialog.exec()

    def open_coincidence_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        # Filter for numeric columns only
        numeric_cols = self.model.dataframe.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            QMessageBox.warning(self.view, "Warning", "No numeric variables found in the dataset.")
            return

        dialog = CoincidenceDialog(self.view, numeric_cols, self._perform_coincidence_calculation)
        dialog.exec()

    def _perform_coincidence_calculation(self, var1, var2, neg1, neg2):
        """Wrapper to perform calculation and log results to the main console."""
        success, result = self.model.calculate_set_coincidence(var1, var2, neg1, neg2)
        if success:
            v1_str = f"~{var1}" if neg1 else var1
            v2_str = f"~{var2}" if neg2 else var2
            msg = f"Set Coincidence ({v1_str}, {v2_str}): {result:.4f}"
            self.append_to_log("SET COINCIDENCE", msg)
        return success, result

    def open_select_if_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        cols = list(self.model.dataframe.columns)
        dialog = SelectIfDialog(self.view, cols)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            condition = dialog.get_condition()
            if not condition:
                return

            success, message = self.model.select_if(condition)
            if success:
                self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
                self.logger.log_action(
                    category="CASE_SELECTION",
                    description=f"Applied case selection filter: {condition}.",
                    metadata={"condition": condition}
                )
                self._reset_analysis_state()
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)

    def cancel_selection(self):
        success, message = self.model.cancel_selection()
        if success:
            self.view.populate_grid(self.model.dataframe, self.model.calibration_metadata)
            self.logger.log_action(
                category="CASE_SELECTION",
                description="Canceled active case selection filter and restored all cases."
            )
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.warning(self.view, "Warning", message)

    def open_sensitivity_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return

        dialog = SensitivityDialog(self.view, self.model)
        dialog.exec()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
