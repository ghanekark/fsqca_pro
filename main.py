import sys
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QInputDialog, QProgressDialog, QDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from views.main_window import MainWindow
from views.analysis_results_dialog import AnalysisResultsDialog
from views.calibration_dialog import CalibrationDialog
from views.compute_dialog import ComputeDialog
from views.necessity_dialog import NecessityDialog
from views.truth_table_dialog import VariableSelectionDialog, EditTruthTableDialog, DeleteAndCodeDialog
from views.assumptions_dialog import AssumptionsDialog
from views.sensitivity_dialog import SensitivityDialog
from models.data_model import QCADataModel
from utils.worker import AnalysisWorker

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        self.model = QCADataModel()
        self.view = MainWindow()
        
        self.current_tt_df = None
        self.current_conditions = None
        self.current_outcome = None
        self.tt_edit_dialog = None
        
        self._setup_connections()
        
    def _setup_connections(self):
        # Bind View actions directly to Controller methods
        self.view.action_open.triggered.connect(self.open_file)
        self.view.action_save.triggered.connect(self.save_file)
        self.view.action_exit.triggered.connect(self.view.close)
        
        self.view.action_compute.triggered.connect(self.open_compute_dialog)
        self.view.action_calibrate.triggered.connect(self.open_calibration_dialog)
        self.view.action_truth_table.triggered.connect(self.open_truth_table_dialog)
        self.view.action_necessity.triggered.connect(self.open_necessity_dialog)
        self.view.action_standard_analysis.triggered.connect(self.open_standard_analysis)
        self.view.action_sensitivity.triggered.connect(self.open_sensitivity_dialog)

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

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
                self.view.populate_grid(self.model.dataframe)
                self._reset_analysis_state()
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
                QMessageBox.information(self.view, "Success", message)
            else:
                QMessageBox.critical(self.view, "Error", message)

    def _reset_analysis_state(self):
        self.current_tt_df = None
        self.current_conditions = None
        self.current_outcome = None

    def open_compute_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return
            
        cols = list(self.model.dataframe.columns)
        dialog = ComputeDialog(self.view, cols, self._perform_compute)
        dialog.exec()

    def _perform_compute(self, target_col, expression):
        success, message = self.model.compute_variable(target_col, expression)
        if success:
            self.view.populate_grid(self.model.dataframe)
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.critical(self.view, "Error", message)

    def open_calibration_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return
            
        cols = list(self.model.dataframe.columns)
        dialog = CalibrationDialog(self.view, cols, self._perform_calibration, 
                                   self.model.auto_calculate_thresholds, self._perform_batch_calibration)
        dialog.exec()

    def _perform_calibration(self, source_col, new_col, p_full, p_cross, p_non):
        success, message = self.model.calibrate_variable(source_col, new_col, p_full, p_cross, p_non)
        if success:
            self.view.populate_grid(self.model.dataframe)
            self._reset_analysis_state() # Calibration might affect TT
            QMessageBox.information(self.view, "Success", message)
        else:
            QMessageBox.critical(self.view, "Error", message)

    def _perform_batch_calibration(self):
        success, message = self.model.auto_calibrate_all()
        if success:
            self.view.populate_grid(self.model.dataframe)
            self._reset_analysis_state()
            QMessageBox.information(self.view, "Batch Calibration", message)
        else:
            QMessageBox.critical(self.view, "Error", message)

    def open_truth_table_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return
            
        cols = list(self.model.dataframe.columns)
        dialog = VariableSelectionDialog(self.view, cols, self._on_tt_generate)
        dialog.exec()

    def _on_tt_generate(self, conditions, outcome):
        try:
            self.current_conditions = conditions
            self.current_outcome = outcome
            self.current_tt_df = self.model.generate_truth_table(conditions, outcome)
            
            if self.current_tt_df is not None:
                self.tt_edit_dialog = EditTruthTableDialog(self.view, self.current_tt_df, self.model, self.open_standard_analysis, self._on_delete_and_code)
                self.tt_edit_dialog.show()
            
            return self.current_tt_df
        except ValueError as e:
            QMessageBox.critical(self.view, "Truth Table Error", str(e))
            return None

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
            results = self.model.run_standard_analysis(self.current_tt_df, freq_thresh, consist_thresh, assumptions)
            
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
        self.worker.start()

    def _on_analysis_finished(self, results):
        self.progress_dialog.close()
        dialog = AnalysisResultsDialog(self.view, results)
        dialog.exec()

    def _on_analysis_error(self, err):
        self.progress_dialog.close()
        QMessageBox.critical(self.view, "Analysis Error", err)

    def open_necessity_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return
            
        cols = list(self.model.dataframe.columns)
        dialog = NecessityDialog(self.view, cols, self.model.calculate_necessary_conditions)
        dialog.exec()

    def open_sensitivity_dialog(self):
        if self.model.dataframe is None:
            QMessageBox.warning(self.view, "Warning", "Please load a dataset first.")
            return
            
        dialog = SensitivityDialog(self.view, self.model)
        dialog.exec()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
