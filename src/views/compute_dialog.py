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

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QLineEdit, QPushButton, QLabel, QMessageBox

class ComputeDialog(QDialog):
    def __init__(self, parent, column_names, submit_callback):
        super().__init__(parent)
        self.setWindowTitle("Compute Variable")
        self.resize(400, 400)
        
        self.column_names = column_names
        self.submit_callback = submit_callback
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Existing Variables (Double-click to insert):"))
        
        # List widget for reference
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.column_names)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)
            
        layout.addWidget(QLabel("Target Variable:"))
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderLabel = "e.g., NEW_VAR"
        layout.addWidget(self.target_edit)
        
        layout.addWidget(QLabel("Expression (e.g., A + B, A * 0.5):"))
        self.expr_edit = QLineEdit()
        self.expr_edit.setPlaceholderLabel = "Enter expression"
        layout.addWidget(self.expr_edit)
        
        self.compute_btn = QPushButton("Compute")
        self.compute_btn.clicked.connect(self._handle_compute)
        layout.addWidget(self.compute_btn)

    def _on_item_double_clicked(self, item):
        # Convenience: double-click variable to append to expression
        current_text = self.expr_edit.text()
        self.expr_edit.setText(current_text + item.text())

    def _handle_compute(self):
        target = self.target_edit.text().strip()
        expr = self.expr_edit.text().strip()
        
        if not target or not expr:
            QMessageBox.warning(self, "Warning", "Please provide both target variable and expression.")
            return
            
        self.submit_callback(target, expr)
        self.accept()
