from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QAbstractItemView, QComboBox, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QCheckBox)

class NecessityDialog(QDialog):
    def __init__(self, parent, column_names, on_analyze):
        super().__init__(parent)
        self.setWindowTitle("Necessary Conditions Analysis")
        self.resize(800, 600)
        self.column_names = column_names
        self.on_analyze = on_analyze
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Builder Layout (Dual Pane)
        builder_layout = QHBoxLayout()

        # Left: Available Conditions
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available Conditions:"))
        self.available_list = QListWidget()
        self.available_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        # Add both positive and negated versions
        for col in self.column_names:
            self.available_list.addItem(col)
            self.available_list.addItem(f"~{col}")
        available_layout.addWidget(self.available_list)
        builder_layout.addLayout(available_layout)

        # Middle: Add Buttons
        mid_btns = QVBoxLayout()
        mid_btns.addStretch()
        
        self.btn_add = QPushButton("Add >")
        self.btn_add.clicked.connect(self._on_add)
        mid_btns.addWidget(self.btn_add)
        
        self.btn_add_or = QPushButton("Add as OR (+) >")
        self.btn_add_or.clicked.connect(self._on_add_or)
        mid_btns.addWidget(self.btn_add_or)

        self.btn_remove = QPushButton("< Remove")
        self.btn_remove.clicked.connect(self._on_remove)
        mid_btns.addWidget(self.btn_remove)
        
        mid_btns.addStretch()
        builder_layout.addLayout(mid_btns)

        # Right: Conditions to Test
        test_layout = QVBoxLayout()
        test_layout.addWidget(QLabel("Conditions to Test:"))
        self.test_list = QListWidget()
        self.test_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        test_layout.addWidget(self.test_list)
        builder_layout.addLayout(test_layout)

        layout.addLayout(builder_layout)

        # Outcome Selection and Analyze Button
        footer_layout = QHBoxLayout()
        
        footer_layout.addWidget(QLabel("Outcome:"))
        self.outcome_combo = QComboBox()
        self.outcome_combo.addItems(self.column_names)
        footer_layout.addWidget(self.outcome_combo)
        
        self.negate_checkbox = QCheckBox("Negate Outcome (~)")
        footer_layout.addWidget(self.negate_checkbox)
        
        footer_layout.addStretch()
        
        self.analyze_btn = QPushButton("Analyze Necessity")
        self.analyze_btn.setStyleSheet("font-weight: bold; padding: 5px;")
        self.analyze_btn.clicked.connect(self._handle_analyze)
        footer_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(footer_layout)

        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Condition Expression', 'Consistency', 'Coverage'])
        layout.addWidget(self.table)

    def _on_add(self):
        selected = self.available_list.selectedItems()
        for item in selected:
            self.test_list.addItem(item.text())

    def _on_add_or(self):
        selected = [item.text() for item in self.available_list.selectedItems()]
        if len(selected) < 2:
            QMessageBox.information(self, "Info", "Select at least two conditions to create an OR (+) expression.")
            return
        
        expr = " + ".join(selected)
        self.test_list.addItem(expr)

    def _on_remove(self):
        selected = self.test_list.selectedItems()
        for item in selected:
            self.test_list.takeItem(self.test_list.row(item))

    def _handle_analyze(self):
        # Gather all expressions from test_list
        conditions = [self.test_list.item(i).text() for i in range(self.test_list.count())]
        outcome = self.outcome_combo.currentText()
        negate_outcome = self.negate_checkbox.isChecked()

        if not conditions or not outcome:
            QMessageBox.warning(self, "Warning", "Please add conditions to test and select an outcome.")
            return

        df_result = self.on_analyze(conditions, outcome, negate_outcome)
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
