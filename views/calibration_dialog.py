from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel

class CalibrationDialog(QDialog):
    def __init__(self, parent, column_names, on_apply, auto_calc_callback, batch_calc_callback):
        super().__init__(parent)
        self.setWindowTitle("Calibrate Variable")
        self.resize(400, 350)
        
        self.column_names = column_names
        self.on_apply = on_apply
        self.auto_calc_callback = auto_calc_callback
        self.batch_calc_callback = batch_calc_callback
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Source Column
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.column_names)
        
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.source_combo)
        
        self.auto_btn = QPushButton("Auto-Calc")
        self.auto_btn.clicked.connect(self._handle_auto_calc)
        source_layout.addWidget(self.auto_btn)
        
        form_layout.addRow("Source Column:", source_layout)

        # New Column Name
        self.new_col_edit = QLineEdit()
        form_layout.addRow("New Column Name:", self.new_col_edit)

        # Thresholds
        self.p_full_edit = QLineEdit()
        form_layout.addRow("Full Membership:", self.p_full_edit)

        self.p_cross_edit = QLineEdit()
        form_layout.addRow("Crossover Point:", self.p_cross_edit)

        self.p_non_edit = QLineEdit()
        form_layout.addRow("Non-Membership:", self.p_non_edit)

        layout.addLayout(form_layout)

        # Single Calibration Apply Button
        self.apply_btn = QPushButton("Apply Single Calibration")
        self.apply_btn.clicked.connect(self._handle_apply)
        layout.addWidget(self.apply_btn)
        
        layout.addSpacing(10)
        
        # Batch Auto-Calibration Button
        self.batch_btn = QPushButton("Auto-Calibrate All Numeric")
        self.batch_btn.setStyleSheet("font-weight: bold; background-color: #e1f5fe;")
        self.batch_btn.clicked.connect(self._handle_batch)
        layout.addWidget(self.batch_btn)

    def _handle_auto_calc(self):
        source_col = self.source_combo.currentText()
        if not source_col:
            return
            
        thresholds = self.auto_calc_callback(source_col)
        if thresholds:
            p_full, p_cross, p_non = thresholds
            
            self.p_full_edit.setText(f"{p_full:.4f}")
            self.p_cross_edit.setText(f"{p_cross:.4f}")
            self.p_non_edit.setText(f"{p_non:.4f}")
            
            # Suggest new column name
            self.new_col_edit.setText(f"f_{source_col}")
        else:
            QMessageBox.warning(self, "Warning", "Could not calculate thresholds for this column.")

    def _handle_apply(self):
        try:
            source_col = self.source_combo.currentText()
            new_col = self.new_col_edit.text().strip()
            p_full = float(self.p_full_edit.text())
            p_cross = float(self.p_cross_edit.text())
            p_non = float(self.p_non_edit.text())
            
            if not new_col:
                raise ValueError("New column name is required.")
                
            self.on_apply(source_col, new_col, p_full, p_cross, p_non)
            self.accept() # Close dialog with success
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid input: {str(e)}")

    def _handle_batch(self):
        self.batch_calc_callback()
        self.accept()
