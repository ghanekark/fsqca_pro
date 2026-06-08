
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QLineEdit, QPushButton, 
                             QDialogButtonBox, QMessageBox, 
                             QAbstractItemView)

class SubsetDialog(QDialog):
    def __init__(self, parent, column_names, on_analyze):
        super().__init__(parent)
        self.setWindowTitle("Select Variables (Subset Analysis)")
        self.resize(700, 500)
        self.column_names = column_names
        self.on_analyze = on_analyze
        
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Horizontal Three-Column Layout
        cols_layout = QHBoxLayout()
        
        # --- Left Column: Source Variables ---
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel("Variables:"))
        self.var_list = QListWidget()
        self.var_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.var_list.addItems(self.column_names)
        left_col.addWidget(self.var_list)
        cols_layout.addLayout(left_col, 2)
        
        # --- Middle Column: Action Buttons ---
        mid_col = QVBoxLayout()
        mid_col.addStretch()
        
        # Set Outcome section
        self.btn_set = QPushButton("Set >")
        self.btn_set_negated = QPushButton("Set Negated (~) >")
        mid_col.addWidget(self.btn_set)
        mid_col.addWidget(self.btn_set_negated)
        
        mid_col.addSpacing(40) # Distinct separation
        
        # Add Conditions section
        self.btn_add = QPushButton("Add >")
        self.btn_add_negated = QPushButton("Add Negated (~) >")
        mid_col.addWidget(self.btn_add)
        mid_col.addWidget(self.btn_add_negated)
        
        mid_col.addStretch()
        cols_layout.addLayout(mid_col, 1)
        
        # --- Right Column: Targeted Inputs ---
        right_col = QVBoxLayout()
        
        # Outcome field
        right_col.addWidget(QLabel("Outcome:"))
        self.outcome_edit = QLineEdit()
        self.outcome_edit.setReadOnly(True)
        self.outcome_edit.setPlaceholderText("Select variable and click 'Set'")
        right_col.addWidget(self.outcome_edit)
        
        right_col.addSpacing(10)
        
        # Conditions list
        right_col.addWidget(QLabel("Causal Conditions:"))
        self.cond_list = QListWidget()
        right_col.addWidget(self.cond_list)
        
        # Clear button for conditions
        self.btn_clear = QPushButton("Clear Conditions")
        self.btn_clear.clicked.connect(self.cond_list.clear)
        right_col.addWidget(self.btn_clear)
        
        cols_layout.addLayout(right_col, 2)
        
        main_layout.addLayout(cols_layout)
        
        # --- Connections ---
        self.btn_set.clicked.connect(self._on_set)
        self.btn_set_negated.clicked.connect(self._on_set_negated)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_add_negated.clicked.connect(self._on_add_negated)
        
        # --- Bottom: Standard Controls ---
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._handle_ok)
        self.buttons.rejected.connect(self.reject)
        main_layout.addWidget(self.buttons)

    def _on_set(self):
        item = self.var_list.currentItem()
        if item:
            self.outcome_edit.setText(item.text())

    def _on_set_negated(self):
        item = self.var_list.currentItem()
        if item:
            self.outcome_edit.setText(f"~{item.text()}")

    def _on_add(self):
        items = self.var_list.selectedItems()
        for item in items:
            # Check for duplicates before adding
            existing = [self.cond_list.item(i).text() for i in range(self.cond_list.count())]
            if item.text() not in existing:
                self.cond_list.addItem(item.text())

    def _on_add_negated(self):
        items = self.var_list.selectedItems()
        for item in items:
            negated_text = f"~{item.text()}"
            existing = [self.cond_list.item(i).text() for i in range(self.cond_list.count())]
            if negated_text not in existing:
                self.cond_list.addItem(negated_text)

    def _handle_ok(self):
        outcome_text = self.outcome_edit.text()
        if not outcome_text or outcome_text.startswith("Select variable"):
            QMessageBox.warning(self, "Warning", "Please set an outcome.")
            return
            
        negate_outcome = False
        clean_outcome = outcome_text
        if outcome_text.startswith('~'):
            negate_outcome = True
            clean_outcome = outcome_text[1:]
            
        conditions = [self.cond_list.item(i).text() for i in range(self.cond_list.count())]
        if not conditions:
            QMessageBox.warning(self, "Warning", "Please add at least one causal condition.")
            return
            
        # Execute the provided callback
        self.on_analyze(conditions, clean_outcome, negate_outcome)
        self.accept()
