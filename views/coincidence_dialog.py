
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QCheckBox, QGroupBox, QDialogButtonBox)

class CoincidenceDialog(QDialog):
    def __init__(self, parent, column_names):
        super().__init__(parent)
        self.setWindowTitle("Set Coincidence")
        self.resize(400, 250)
        self.column_names = column_names
        
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
        
        # --- Buttons ---
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_selections(self):
        """Returns (var1, var2, negate1, negate2)"""
        return (
            self.combo_x.currentText(),
            self.combo_y.currentText(),
            self.negate_x.isChecked(),
            self.negate_y.isChecked()
        )
