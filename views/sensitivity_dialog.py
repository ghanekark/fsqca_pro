from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QDoubleSpinBox, QPushButton, QTextEdit
import numpy as np

class SensitivityDialog(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setWindowTitle("Sensitivity Analysis")
        self.resize(500, 600)
        self.model = model
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.col_combo = QComboBox()
        if self.model.dataframe is not None:
            # show columns that don't start with f_ and aren't outcome_code
            raw_cols = [c for c in self.model.dataframe.columns if not c.startswith('f_') and c != 'outcome_code']
            self.col_combo.addItems(raw_cols)
        layout.addWidget(self.col_combo)
        
        form_layout = QFormLayout()
        self.p_full_spin = QDoubleSpinBox()
        self.p_cross_spin = QDoubleSpinBox()
        self.p_non_spin = QDoubleSpinBox()
        
        for spin in (self.p_full_spin, self.p_cross_spin, self.p_non_spin):
            spin.setRange(-9999999, 9999999)
            spin.setDecimals(4)
            
        form_layout.addRow("Full Membership (p_full):", self.p_full_spin)
        form_layout.addRow("Crossover (p_cross):", self.p_cross_spin)
        form_layout.addRow("Non-Membership (p_non):", self.p_non_spin)
        
        layout.addLayout(form_layout)
        
        self.sim_btn = QPushButton("Simulate Sensitivity")
        self.sim_btn.clicked.connect(self._handle_simulate)
        layout.addWidget(self.sim_btn)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

    def _handle_simulate(self):
        raw_col = self.col_combo.currentText()
        if not raw_col:
            return
            
        p_full = self.p_full_spin.value()
        p_cross = self.p_cross_spin.value()
        p_non = self.p_non_spin.value()
        
        # 1) Calibrate to f_temp
        success, msg = self.model.calibrate_variable(raw_col, 'f_temp', p_full, p_cross, p_non)
        if not success:
            self.result_text.setPlainText(f"Calibration failed: {msg}")
            return
            
        # 2) Gather existing f_ columns
        f_cols = [c for c in self.model.dataframe.columns if c.startswith('f_') and c != 'f_temp']
        if not f_cols:
            self.result_text.setPlainText("No fuzzy columns found to use as conditions/outcome.")
            return
            
        outcome = 'f_survival' if 'f_survival' in f_cols else f_cols[-1]
        
        conditions = [c for c in f_cols if c != outcome]
        
        # substitute f_{raw_col} with f_temp
        target_f_col = f"f_{raw_col}"
        if target_f_col in conditions:
            conditions[conditions.index(target_f_col)] = 'f_temp'
        else:
            # If the variable wasn't already a condition, just append it
            conditions.append('f_temp')
            
        # 3) Generate truth table
        try:
            tt_df = self.model.generate_truth_table(conditions, outcome)
            
            # 4) Run standard analysis with freq 1, consist 0.8
            assumptions = {c: "Present or Absent" for c in conditions}
            results = self.model.run_standard_analysis(tt_df, 1, 0.8, assumptions)
            
            # 5) Format and print Parsimonious solution paths
            parsimonious_sol = results.get("parsimonious", [])
            
            if not parsimonious_sol:
                self.result_text.setPlainText("Parsimonious Solution: No paths found.")
                return
                
            report = "--- Parsimonious Solution (Sensitivity) ---\n"
            for term in parsimonious_sol:
                parts = []
                for i, char in enumerate(term):
                    if char == '1':
                        parts.append(conditions[i])
                    elif char == '0':
                        parts.append(f"~{conditions[i]}")
                path_str = "*".join(parts) if parts else "1"
                report += f"{path_str}\n"
                
            self.result_text.setPlainText(report)
            
        except ValueError as e:
            self.result_text.setPlainText(f"Analysis Error: {str(e)}")
        except Exception as e:
            self.result_text.setPlainText(f"Unexpected Error: {str(e)}")
