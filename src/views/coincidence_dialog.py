
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QGroupBox, QDialogButtonBox, QPushButton)
from PyQt6.QtCore import Qt

class CoincidenceDialog(QDialog):
    def __init__(self, parent, column_names, calculate_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Set Coincidence Diagnostic")
        self.resize(450, 300)
        self.column_names = column_names
        self.calculate_callback = calculate_callback
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Set X Group ---
        group_x = QGroupBox("Set X")
        layout_x = QHBoxLayout(group_x)
        self.combo_x = QComboBox()
        self.combo_x.addItems(self.column_names)
        self.negate_x = QCheckBox("Negate (~)")
        layout_x.addWidget(QLabel("Variable:"))
        layout_x.addWidget(self.combo_x)
        layout_x.addWidget(self.negate_x)
        layout.addWidget(group_x)
        
        # --- Set Y Group ---
        group_y = QGroupBox("Set Y")
        layout_y = QHBoxLayout(group_y)
        self.combo_y = QComboBox()
        self.combo_y.addItems(self.column_names)
        self.negate_y = QCheckBox("Negate (~)")
        layout_y.addWidget(QLabel("Variable:"))
        layout_y.addWidget(self.combo_y)
        layout_y.addWidget(self.negate_y)
        layout.addWidget(group_y)

        # --- Result Section ---
        self.result_group = QGroupBox("Diagnostic Result")
        res_layout = QVBoxLayout(self.result_group)
        self.result_label = QLabel("Coincidence Score: ---")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setObjectName("ResultLabel")
        res_layout.addWidget(self.result_label)
        layout.addWidget(self.result_group)
        
        # --- Action Buttons ---
        btn_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("Calculate Coincidence")
        self.calculate_btn.setObjectName("PrimaryButton")
        self.calculate_btn.clicked.connect(self._on_calculate)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.calculate_btn)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

    def _on_calculate(self):
        """Triggers the calculation via the provided callback and updates the UI."""
        if self.calculate_callback:
            var1, var2, neg1, neg2 = self.get_selections()
            success, result = self.calculate_callback(var1, var2, neg1, neg2)
            if success:
                self.result_label.setText(f"Coincidence Score: {result:.4f}")
            else:
                self.result_label.setText(f"Error: {result}")

    def get_selections(self):
        """Returns (var1, var2, negate1, negate2)"""
        return (
            self.combo_x.currentText(),
            self.combo_y.currentText(),
            self.negate_x.isChecked(),
            self.negate_y.isChecked()
        )
