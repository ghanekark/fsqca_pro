from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QAbstractItemView, QComboBox, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QGroupBox, QMenuBar,
                             QDialogButtonBox, QSpinBox, QDoubleSpinBox,
                             QRadioButton, QButtonGroup, QGridLayout,
                             QCheckBox, QScrollArea, QWidget, QFileDialog)
from PyQt6.QtGui import QAction, QKeySequence
import numpy as np
from utils.formatter import ResultFormatter

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

        # Negate Outcome Checkbox
        self.negate_checkbox = QCheckBox("Negate Outcome (~)")
        layout.addWidget(self.negate_checkbox)

        # Generate Button
        self.gen_btn = QPushButton("Generate Truth Table")
        self.gen_btn.clicked.connect(self._handle_generate)
        layout.addWidget(self.gen_btn)

    def _handle_generate(self):
        selected_items = self.cond_listbox.selectedItems()
        conditions = [item.text() for item in selected_items]
        outcome = self.outcome_combo.currentText()
        negate_outcome = self.negate_checkbox.isChecked()

        if not conditions or not outcome:
            QMessageBox.warning(self, "Warning", "Please select conditions and an outcome.")
            return

        self.on_generate(conditions, outcome, negate_outcome)
        self.accept()

class EditTruthTableDialog(QDialog):
    def __init__(self, parent, df, model, on_standard_analysis, delete_code_callback, specify_analysis_callback):
        super().__init__(parent)
        self.setWindowTitle("Edit Truth Table & Run Analysis")
        self.resize(1100, 700)
        self.df = df
        self.model = model
        self.on_standard_analysis = on_standard_analysis
        self.delete_code_callback = delete_code_callback
        self.specify_analysis_callback = specify_analysis_callback
        
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

        # Export Button
        self.export_btn = QPushButton("Export Table")
        self.export_btn.clicked.connect(self._on_export)
        toolbar_layout.addWidget(self.export_btn)

        # Specify Analysis Button
        self.specify_btn = QPushButton("Specify Analysis")
        self.specify_btn.clicked.connect(self.specify_analysis_callback)
        toolbar_layout.addWidget(self.specify_btn)

        # Analysis Button
        self.analysis_btn = QPushButton("Standard Analyses")
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

    def _on_export(self):
        filepath, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Truth Table", "", "Text Document (*.txt);;CSV Files (*.csv)"
        )
        if not filepath:
            return

        try:
            if "CSV" in selected_filter:
                if not filepath.lower().endswith(".csv"):
                    filepath += ".csv"
                content = ResultFormatter.format_truth_table_csv(self.model.truth_table_df)
            else:
                if not filepath.lower().endswith(".txt"):
                    filepath += ".txt"
                content = self.model.truth_table_df.to_string(index=False)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            QMessageBox.information(self, "Success", f"Truth table successfully exported to:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not export file: {str(e)}")

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

class SpecifyAnalysisDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Specify Analysis")
        self.setMinimumWidth(450)
        
        self.groups = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        instruction = QLabel("Specify how each type of truth table configuration should be treated in the analysis:")
        instruction.setWordWrap(True)
        layout.addWidget(instruction)
        
        grid = QGridLayout()
        layout.addLayout(grid)
        
        # Mapping for display labels to internal keys and default values
        self.categories = [
            ("Positive Cases (1)", "1", "True"),
            ("Negative Cases (0)", "0", "False"),
            ("Don't Care Cases (-)", "-", "False"),
            ("Remainders", "rem", "False")
        ]
        
        options = ["True", "False", "Don't Cares"]
        
        # Add Header
        for i, opt in enumerate(options):
            grid.addWidget(QLabel(f"<b>{opt}</b>"), 0, i + 1)

        for row_idx, (cat_label, cat_key, default) in enumerate(self.categories, start=1):
            grid.addWidget(QLabel(cat_label), row_idx, 0)
            
            bg = QButtonGroup(self)
            self.groups[cat_key] = bg
            
            for col_idx, opt in enumerate(options, start=1):
                rb = QRadioButton()
                bg.addButton(rb)
                grid.addWidget(rb, row_idx, col_idx)
                
                if opt == default:
                    rb.setChecked(True)
                
                # Store the option string in the button's property
                rb.setProperty("option", opt)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_configuration(self):
        """
        Returns a dictionary mapping '1', '0', '-', and 'rem' 
        to 'True', 'False', or 'Don't Cares'.
        """
        config = {}
        for cat_key, bg in self.groups.items():
            checked_button = bg.checkedButton()
            if checked_button:
                config[cat_key] = checked_button.property("option")
        return config

class PrimeImplicantChartDialog(QDialog):
    def __init__(self, parent, tied_pis, conditions):
        super().__init__(parent)
        self.setWindowTitle("Prime Implicant Chart")
        self.setMinimumSize(450, 400)
        self.tied_pis = tied_pis
        self.conditions = conditions
        self.checkbox_mapping = {}
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Some prime implicants are tied. Use the checkboxes to select which prime implicants to keep.")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Scroll Area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        
        for pi in self.tied_pis:
            # Build a readable label: 1 -> A, 0 -> ~A, - -> skip
            parts = []
            for i, char in enumerate(pi):
                if char == '1':
                    parts.append(self.conditions[i])
                elif char == '0':
                    parts.append(f"~{self.conditions[i]}")
            
            readable_label = " ".join(parts) if parts else "Empty set (1)"
            
            cb = QCheckBox(readable_label)
            cb.setChecked(True) # Default to all selected
            self.checkbox_mapping[cb] = pi
            self.scroll_layout.addWidget(cb)
        
        self.scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Select All Button
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._on_select_all)
        layout.addWidget(self.select_all_btn)
        
        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def _on_select_all(self):
        for cb in self.checkbox_mapping.keys():
            cb.setChecked(True)

    def get_selected(self):
        """Returns a list of raw bitstrings for the checked boxes."""
        selected = [raw_pi for cb, raw_pi in self.checkbox_mapping.items() if cb.isChecked()]
        # Failsafe: if nothing is selected or canceled, return everything
        if not selected:
            return self.tied_pis
        return selected
