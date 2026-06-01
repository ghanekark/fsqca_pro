from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont
from views.visual_boolean_dialog import VisualBooleanDialog
from views.solution_continuum_dialog import SolutionContinuumDialog

class AnalysisResultsDialog(QDialog):
    def __init__(self, parent, results):
        super().__init__(parent)
        self.setWindowTitle("Standard Analysis Results")
        self.resize(900, 700)
        self.results = results
        
        self._setup_ui()
        self._format_report()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("QCA Minimization & Metrics Report:"))

        # Text edit with monospaced font
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier New", 10))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.text_edit)

        # Bottom button layout
        btn_layout = QHBoxLayout()
        
        self.visualize_btn = QPushButton("Visualize Configurations")
        self.visualize_btn.clicked.connect(self._handle_visualize)
        btn_layout.addWidget(self.visualize_btn)
        
        self.continuum_btn = QPushButton("View Solution Continuum")
        self.continuum_btn.clicked.connect(self._handle_continuum)
        self.continuum_btn.setStyleSheet("font-weight: bold; color: palette(link);")
        btn_layout.addWidget(self.continuum_btn)
        
        btn_layout.addStretch()

        self.save_btn = QPushButton("Save Report As...")
        self.save_btn.clicked.connect(self._save_report)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def _save_report(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save QCA Report", "", "Text Document (*.txt)"
        )
        if filepath:
            try:
                if not filepath.endswith(".txt"):
                    filepath += ".txt"
                content = self.text_edit.toPlainText()
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                QMessageBox.information(self, "Success", f"Report successfully saved to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def _handle_visualize(self):
        conditions = self.results.get("conditions", [])
        dialog = VisualBooleanDialog(self, self.results, conditions)
        dialog.exec()

    def _handle_continuum(self):
        conditions = self.results.get("conditions", [])
        dialog = SolutionContinuumDialog(self, self.results, conditions)
        dialog.exec()

    def _get_path_string(self, term, conditions):
        parts = []
        for i, char in enumerate(term):
            if char == '1':
                parts.append(conditions[i])
            elif char == '0':
                parts.append(f"~{conditions[i]}")
        return "*".join(parts) if parts else "1"

    def _format_solution_block(self, title, metrics, conditions):
        if not metrics or not metrics.get("term_metrics"):
            return f"--- {title} ---\nNo solution found.\n\n"

        report = f"--- {title} ---\n"
        header = f"{'PATH':<40} | {'RAW COVERAGE':<12} | {'UNIQUE COVERAGE':<15} | {'CONSISTENCY':<11}\n"
        report += header
        report += "-" * len(header) + "\n"

        for tm in metrics["term_metrics"]:
            path = self._get_path_string(tm["term"], conditions)
            report += f"{path:<40} | {tm['raw_coverage']:>12.6f} | {tm['unique_coverage']:>15.6f} | {tm['consistency']:>11.6f}\n"

        report += "-" * len(header) + "\n"
        report += f"solution coverage: {metrics['solution_coverage']:.6f}\n"
        report += f"solution consistency: {metrics['solution_consistency']:.6f}\n\n"
        
        return report

    def _format_report(self):
        conditions = self.results.get("conditions", [])
        complex_metrics = self.results.get("complex_metrics")
        intermediate_metrics = self.results.get("intermediate_metrics")
        parsimonious_metrics = self.results.get("parsimonious_metrics")

        report = "QCA STANDARD ANALYSIS REPORT\n"
        report += "=" * 85 + "\n\n"
        
        report += "CAUSAL CONDITIONS:\n"
        report += ", ".join(conditions) + "\n\n"

        report += self._format_solution_block("COMPLEX SOLUTION", complex_metrics, conditions)
        report += self._format_solution_block("INTERMEDIATE SOLUTION", intermediate_metrics, conditions)
        report += self._format_solution_block("PARSIMONIOUS SOLUTION", parsimonious_metrics, conditions)

        self.text_edit.setPlainText(report)
