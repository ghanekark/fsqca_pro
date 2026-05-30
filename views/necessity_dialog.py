from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QAbstractItemView, QComboBox, 
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox)

class NecessityDialog(QDialog):
    def __init__(self, parent, column_names, on_analyze):
        super().__init__(parent)
        self.setWindowTitle("Necessary Conditions Analysis")
        self.resize(600, 500)
        self.column_names = column_names
        self.on_analyze = on_analyze
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Control Layout
        ctrl_layout = QHBoxLayout()

        # Causal Conditions List
        cond_layout = QVBoxLayout()
        cond_layout.addWidget(QLabel("Causal Conditions:"))
        self.cond_listbox = QListWidget()
        self.cond_listbox.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.cond_listbox.addItems(self.column_names)
        cond_layout.addWidget(self.cond_listbox)
        ctrl_layout.addLayout(cond_layout)

        # Outcome and Button
        out_btn_layout = QVBoxLayout()
        out_btn_layout.addWidget(QLabel("Outcome:"))
        self.outcome_combo = QComboBox()
        self.outcome_combo.addItems(self.column_names)
        out_btn_layout.addWidget(self.outcome_combo)
        
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self._handle_analyze)
        out_btn_layout.addWidget(self.analyze_btn)
        out_btn_layout.addStretch()
        
        ctrl_layout.addLayout(out_btn_layout)
        layout.addLayout(ctrl_layout)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Condition', 'Consistency', 'Coverage'])
        layout.addWidget(self.table)

    def _handle_analyze(self):
        selected_items = self.cond_listbox.selectedItems()
        conditions = [item.text() for item in selected_items]
        outcome = self.outcome_combo.currentText()

        if not conditions or not outcome:
            QMessageBox.warning(self, "Warning", "Please select conditions and an outcome.")
            return

        df_result = self.on_analyze(conditions, outcome)
        if df_result is not None:
            self._populate_table(df_result)

    def _populate_table(self, df):
        self.table.setRowCount(0)
        self.table.setRowCount(len(df))
        
        for row_idx, row in enumerate(df.itertuples(index=False)):
            item_cond = QTableWidgetItem(str(row.Condition))
            item_cons = QTableWidgetItem(f"{row.Consistency:.6f}")
            item_cov = QTableWidgetItem(f"{row.Coverage:.6f}")
            
            self.table.setItem(row_idx, 0, item_cond)
            self.table.setItem(row_idx, 1, item_cons)
            self.table.setItem(row_idx, 2, item_cov)
            
        self.table.resizeColumnsToContents()
