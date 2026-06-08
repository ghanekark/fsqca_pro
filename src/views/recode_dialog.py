
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QRadioButton, QGroupBox, 
                             QPushButton, QListWidget, QDialogButtonBox,
                             QGridLayout, QButtonGroup)

class RecodeDialog(QDialog):
    def __init__(self, parent, column_names):
        super().__init__(parent)
        self.setWindowTitle("Recode Variables")
        self.resize(1000, 600)
        self.column_names = column_names
        
        self.rules_data = [] # Stores dicts for the backend
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
# ... (UI setup is mostly unchanged, but let's ensure we have everything)
        main_layout = QVBoxLayout(self)
        
        # Top: Horizontal layout for the three main columns
        cols_layout = QHBoxLayout()
        
        # --- Left Column: Variable Configuration ---
        left_col = QVBoxLayout()
        
        mode_group = QGroupBox("Target Mode")
        mode_layout = QVBoxLayout(mode_group)
        self.radio_new = QRadioButton("Code new variable")
        self.radio_existing = QRadioButton("Recode existing variable")
        self.radio_new.setChecked(True)
        mode_layout.addWidget(self.radio_new)
        mode_layout.addWidget(self.radio_existing)
        left_col.addWidget(mode_group)
        
        left_col.addWidget(QLabel("Target Variable Name:"))
        self.target_name_edit = QLineEdit()
        left_col.addWidget(self.target_name_edit)
        
        left_col.addWidget(QLabel("Based on (Source):"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.column_names)
        left_col.addWidget(self.source_combo)
        
        left_col.addStretch()
        cols_layout.addLayout(left_col, 1)

        # --- Middle Column: Rule Builder ---
        mid_col = QVBoxLayout()
        
        # Old Values Group
        old_group = QGroupBox("Old Values")
        old_layout = QGridLayout(old_group)
        self.old_bg = QButtonGroup(self)
        
        self.radio_val = QRadioButton("Value:")
        self.edit_val = QLineEdit()
        self.old_bg.addButton(self.radio_val)
        old_layout.addWidget(self.radio_val, 0, 0)
        old_layout.addWidget(self.edit_val, 0, 1)
        
        self.radio_missing = QRadioButton("Missing")
        self.old_bg.addButton(self.radio_missing)
        old_layout.addWidget(self.radio_missing, 1, 0)
        
        self.radio_range = QRadioButton("Range:")
        self.edit_range_min = QLineEdit()
        self.edit_range_max = QLineEdit()
        self.old_bg.addButton(self.radio_range)
        old_layout.addWidget(self.radio_range, 2, 0)
        range_box = QHBoxLayout()
        range_box.addWidget(self.edit_range_min)
        range_box.addWidget(QLabel("thru"))
        range_box.addWidget(self.edit_range_max)
        old_layout.addLayout(range_box, 2, 1)
        
        self.radio_lowest = QRadioButton("Range, LOWEST thru:")
        self.edit_lowest = QLineEdit()
        self.old_bg.addButton(self.radio_lowest)
        old_layout.addWidget(self.radio_lowest, 3, 0)
        old_layout.addWidget(self.edit_lowest, 3, 1)
        
        self.radio_highest = QRadioButton("Range, thru HIGHEST:")
        self.edit_highest = QLineEdit()
        self.old_bg.addButton(self.radio_highest)
        old_layout.addWidget(self.radio_highest, 4, 0)
        old_layout.addWidget(self.edit_highest, 4, 1)
        
        self.radio_otherwise = QRadioButton("All other values")
        self.old_bg.addButton(self.radio_otherwise)
        old_layout.addWidget(self.radio_otherwise, 5, 0)
        
        self.radio_val.setChecked(True)
        mid_col.addWidget(old_group)
        
        # New Values Group
        new_group = QGroupBox("New Value")
        new_layout = QGridLayout(new_group)
        self.new_bg = QButtonGroup(self)
        
        self.radio_new_val = QRadioButton("Value:")
        self.edit_new_val = QLineEdit()
        self.new_bg.addButton(self.radio_new_val)
        new_layout.addWidget(self.radio_new_val, 0, 0)
        new_layout.addWidget(self.edit_new_val, 0, 1)
        
        self.radio_new_missing = QRadioButton("System-missing")
        self.new_bg.addButton(self.radio_new_missing)
        new_layout.addWidget(self.radio_new_missing, 1, 0)
        
        self.radio_new_val.setChecked(True)
        mid_col.addWidget(new_group)
        
        # Rule Action Buttons
        rule_btn_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton("Add Rule")
        self.remove_rule_btn = QPushButton("Remove Selected")
        rule_btn_layout.addWidget(self.add_rule_btn)
        rule_btn_layout.addWidget(self.remove_rule_btn)
        mid_col.addLayout(rule_btn_layout)
        
        mid_col.addStretch()
        cols_layout.addLayout(mid_col, 1)

        # --- Right Column: Rules List ---
        right_col = QVBoxLayout()
        right_col.addWidget(QLabel("Rules (evaluated in order):"))
        self.rules_listbox = QListWidget()
        right_col.addWidget(self.rules_listbox)
        
        cols_layout.addLayout(right_col, 1)
        
        main_layout.addLayout(cols_layout)
        
        # Bottom: OK/Cancel
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

    def _connect_signals(self):
        self.add_rule_btn.clicked.connect(self._on_add_rule)
        self.remove_rule_btn.clicked.connect(self._on_remove_rule)
        self.radio_existing.toggled.connect(self._on_mode_toggled)

    def _on_mode_toggled(self, checked):
        if checked:
            self.target_name_edit.setEnabled(False)
            self.target_name_edit.setText(self.source_combo.currentText())
        else:
            self.target_name_edit.setEnabled(True)

    def _on_add_rule(self):
        rule = {}
        display_str = ""
        
        # 1. Identify Old Value Type
        if self.radio_val.isChecked():
            val = self.edit_val.text()
            try:
                val = float(val) if '.' in val else int(val)
            except: pass
            rule = {'type': 'value', 'old': val}
            display_str = f"{val}"
        elif self.radio_missing.isChecked():
            rule = {'type': 'missing'}
            display_str = "MISSING"
        elif self.radio_range.isChecked():
            v1, v2 = self.edit_range_min.text(), self.edit_range_max.text()
            try:
                v1 = float(v1) if '.' in v1 else int(v1)
                v2 = float(v2) if '.' in v2 else int(v2)
            except: pass
            rule = {'type': 'range', 'min': v1, 'max': v2}
            display_str = f"{v1} thru {v2}"
        elif self.radio_lowest.isChecked():
            v = self.edit_lowest.text()
            try:
                v = float(v) if '.' in v else int(v)
            except: pass
            rule = {'type': 'range_lowest', 'max': v}
            display_str = f"LOWEST thru {v}"
        elif self.radio_highest.isChecked():
            v = self.edit_highest.text()
            try:
                v = float(v) if '.' in v else int(v)
            except: pass
            rule = {'type': 'range_highest', 'min': v}
            display_str = f"{v} thru HIGHEST"
        elif self.radio_otherwise.isChecked():
            rule = {'type': 'otherwise'}
            display_str = "ELSE"

        # 2. Identify New Value
        if self.radio_new_val.isChecked():
            nv = self.edit_new_val.text()
            try:
                nv = float(nv) if '.' in nv else int(nv)
            except: pass
            rule['new'] = nv
            display_str += f" -> {nv}"
        else:
            rule['new'] = 'missing'
            display_str += " -> SYSMIS"

        self.rules_data.append(rule)
        self.rules_listbox.addItem(display_str)

    def _on_remove_rule(self):
        idx = self.rules_listbox.currentRow()
        if idx >= 0:
            self.rules_listbox.takeItem(idx)
            self.rules_data.pop(idx)

    def get_recode_parameters(self):
        source = self.source_combo.currentText()
        if self.radio_existing.isChecked():
            target = source
        else:
            target = self.target_name_edit.text()
        
        return source, target, self.rules_data
