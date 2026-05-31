
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QLineEdit, QDialogButtonBox)

class SelectIfDialog(QDialog):
    def __init__(self, parent, column_names):
        super().__init__(parent)
        self.setWindowTitle("Select Cases If")
        self.resize(500, 300)
        self.column_names = column_names
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Instruction
        instruction = QLabel("Enter a logical condition using pandas syntax (e.g., f_funding > 0.5 & f_outcome < 0.2):")
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        # Middle: Reference List and Input
        mid_layout = QHBoxLayout()
        
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.column_names)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        mid_layout.addWidget(self.list_widget, 1) # Stretch factor 1
        
        self.condition_edit = QLineEdit()
        self.condition_edit.setPlaceholderText("Double-click variable or type condition here...")
        mid_layout.addWidget(self.condition_edit, 2) # Stretch factor 2
        
        layout.addLayout(mid_layout)
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _on_item_double_clicked(self, item):
        current_text = self.condition_edit.text()
        # Add space if there's already text and it doesn't end with one
        if current_text and not current_text.endswith(' '):
            current_text += ' '
        self.condition_edit.setText(current_text + item.text() + ' ')
        self.condition_edit.setFocus()

    def get_condition(self):
        return self.condition_edit.text().strip()
