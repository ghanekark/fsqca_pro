# fsQCA Pro
# Copyright (C) 2026 ImmortalSoft
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont
from views.visual_boolean_dialog import VisualBooleanDialog
from views.solution_continuum_dialog import SolutionContinuumDialog
from utils.formatter import ResultFormatter

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
        self.continuum_btn.setObjectName("LinkButton")
        btn_layout.addWidget(self.continuum_btn)
        
        btn_layout.addStretch()

        self.save_btn = QPushButton("Save Report As...")
        self.save_btn.clicked.connect(self._save_report)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

    def _save_report(self):
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Save QCA Report", "", "Text Document (*.txt);;CSV Files (*.csv)"
        )
        if not filepath:
            return

        try:
            if "CSV" in selected_filter:
                if not filepath.lower().endswith(".csv"):
                    filepath += ".csv"
                # For CSV, we use the structured formatter
                outcome_name = self.results.get("outcome_name", "Unknown")
                content = ResultFormatter.format_standard_analysis_csv(self.results, outcome_name)
            else:
                if not filepath.lower().endswith(".txt"):
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

    def _format_report(self):
        outcome_name = self.results.get("outcome_name", "Unknown")
        report = ResultFormatter.format_standard_analysis(self.results, outcome_name)
        self.text_edit.setPlainText(report)

