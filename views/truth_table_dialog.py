from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QAbstractItemView, QComboBox, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QGroupBox, QMenuBar,
                             QDialogButtonBox, QSpinBox, QDoubleSpinBox)
from PyQt6.QtGui import QAction, QKeySequence
import numpy as np

class VariableSelectionDialog(QDialog):
    def __init__(self, parent, column_names, on_generate):
        super().__init__(parent)
        self.setWindowTitle("Truth Table Variable Selection")
        self.resize(400, 500)
        self.column_names = column_names
        self.on_generate = on_generate
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Causal Conditions
        layout.addWidget(QLabel("Select Causal Conditions:"))
        self.cond_listbox = QListWidget()
        self.cond_listbox.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.cond_listbox.addItems(self.column_names)
        layout.addWidget(self.cond_listbox)

        # Outcome
        layout.addWidget(QLabel("Select Outcome:"))
        self.outcome_combo = QComboBox()
        self.outcome_combo.addItems(self.column_names)
        layout.addWidget(self.outcome_combo)

        # Generate Button
        self.gen_btn = QPushButton("Generate Truth Table")
        self.gen_btn.clicked.connect(self._handle_generate)
        layout.addWidget(self.gen_btn)

    def _handle_generate(self):
        selected_items = self.cond_listbox.selectedItems()
        conditions = [item.text() for item in selected_items]
        outcome = self.outcome_combo.currentText()

        if not conditions or not outcome:
            QMessageBox.warning(self, "Warning", "Please select conditions and an outcome.")
            return

        self.on_generate(conditions, outcome)
        self.accept()

class EditTruthTableDialog(QDialog):
    def __init__(self, parent, df, model, on_standard_analysis, delete_code_callback):
        super().__init__(parent)
        self.setWindowTitle("Edit Truth Table & Run Analysis")
        self.resize(1100, 700)
        self.df = df
        self.model = model
        self.on_standard_analysis = on_standard_analysis
        self.delete_code_callback = delete_code_callback
        
        self._setup_ui()
        self.refresh_grid(df)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Menu Bar
        menubar = QMenuBar()
        edit_menu = menubar.addMenu("&Edit")
        
        del_row_act = QAction("Delete current row", self)
        del_row_act.triggered.connect(self._on_delete_row)
        edit_menu.addAction(del_row_act)
        
        del_to_end_act = QAction("Delete current row to last row", self)
        del_to_end_act.triggered.connect(self._on_delete_to_end)
        edit_menu.addAction(del_to_end_act)
        
        del_from_start_act = QAction("Delete first row to current row", self)
        del_from_start_act.triggered.connect(self._on_delete_from_start)
        edit_menu.addAction(del_from_start_act)
        
        edit_menu.addSeparator()
        
        del_code_act = QAction("Delete and code...", self)
        del_code_act.setShortcut(QKeySequence("Ctrl+D"))
        del_code_act.triggered.connect(self.delete_code_callback)
        edit_menu.addAction(del_code_act)
        
        layout.setMenuBar(menubar)

        # Truth Table View
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Toolbar Frame
        toolbar_layout = QHBoxLayout()

        # Overrides Group
        edit_group = QGroupBox("Manual Overrides")
        edit_layout = QHBoxLayout(edit_group)

        edit_layout.addWidget(QLabel("Set Outcome for Selected:"))
        self.override_combo = QComboBox()
        self.override_combo.addItems(['1', '0', '-', ''])
        self.override_combo.setCurrentIndex(3)
        edit_layout.addWidget(self.override_combo)
        
        self.apply_btn = QPushButton("Apply Override")
        self.apply_btn.clicked.connect(self._handle_override)
        edit_layout.addWidget(self.apply_btn)
        
        toolbar_layout.addWidget(edit_group)

        # Analysis Button
        self.analysis_btn = QPushButton("Standard Analyses")
        self.analysis_btn.setStyleSheet("font-weight: bold; padding: 10px; background-color: #e8f5e9;")
        self.analysis_btn.clicked.connect(self.on_standard_analysis)
        toolbar_layout.addWidget(self.analysis_btn)

        layout.addLayout(toolbar_layout)

    def refresh_grid(self, df):
        self.table.setRowCount(0)
        cols = list(df.columns)
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setRowCount(len(df))
        
        for row_idx, row in enumerate(df.itertuples(index=False)):
            for col_idx, val in enumerate(row):
                if isinstance(val, (float, np.float64)):
                    item = QTableWidgetItem(f"{val:.3f}")
                else:
                    item = QTableWidgetItem(str(val))
                self.table.setItem(row_idx, col_idx, item)
                
        self.table.resizeColumnsToContents()

    def _on_delete_row(self):
        row = self.table.currentRow()
        if row >= 0:
            if self.model.delete_truth_table_row(row):
                self.refresh_grid(self.model.truth_table_df)

    def _on_delete_to_end(self):
        row = self.table.currentRow()
        if row >= 0:
            if self.model.delete_truth_table_rows_to_end(row):
                self.refresh_grid(self.model.truth_table_df)

    def _on_delete_from_start(self):
        row = self.table.currentRow()
        if row >= 0:
            if self.model.delete_truth_table_rows_from_start(row):
                self.refresh_grid(self.model.truth_table_df)

    def _handle_override(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges:
            return
        
        new_val = self.override_combo.currentText()
        cols = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        
        if 'outcome_code' not in cols:
            return
            
        out_idx = cols.index('outcome_code')
        
        selected_rows = set()
        for r in selected_ranges:
            for row_idx in range(r.topRow(), r.bottomRow() + 1):
                selected_rows.add(row_idx)
                
        for row_idx in selected_rows:
            item = QTableWidgetItem(new_val)
            self.table.setItem(row_idx, out_idx, item)
            self.model.edit_truth_table_row(row_idx, new_val)

class DeleteAndCodeDialog(QDialog):
    def __init__(self, parent, outcome_name):
        super().__init__(parent)
        self.setWindowTitle("Delete and Code")
        self.resize(450, 150)
        
        layout = QVBoxLayout(self)

        # Frequency Row
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Delete rows with number less than"))
        self.freq_spin = QSpinBox()
        self.freq_spin.setMinimum(1)
        self.freq_spin.setValue(1)
        freq_layout.addWidget(self.freq_spin)
        layout.addLayout(freq_layout)

        # Consistency Row
        consist_layout = QHBoxLayout()
        consist_layout.addWidget(QLabel(f"and set {outcome_name} to 1 for rows with consist >"))
        self.consist_spin = QDoubleSpinBox()
        self.consist_spin.setRange(0.0, 1.0)
        self.consist_spin.setSingleStep(0.01)
        self.consist_spin.setValue(0.8)
        consist_layout.addWidget(self.consist_spin)
        layout.addLayout(consist_layout)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_frequency(self):
        return self.freq_spin.value()

    def get_consistency(self):
        return self.consist_spin.value()
