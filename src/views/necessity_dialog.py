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

from typing import List, Optional, Callable
import pandas as pd
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QAbstractItemView, QComboBox, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QMessageBox, QCheckBox, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal

class NecessityDialog(QDialog):
    """
    Dialog for performing Necessary Conditions Analysis.
    
    Allows researchers to test individual conditions or complex OR (+) expressions
    against an outcome. Includes advanced auditing metrics like RoN and Triviality.
    """
    
    # Signal emitted when the user requests an analysis
    # (conditions, outcome, negate_outcome)
    analyze_requested = pyqtSignal(list, str, bool)

    def __init__(self, parent: Optional[QWidget], column_names: List[str]) -> None:
        """
        Initializes the NecessityDialog.

        Args:
            parent: The parent widget.
            column_names: List of available variables in the dataset.
        """
        super().__init__(parent)
        self.setWindowTitle("Necessary Conditions Analysis")
        self.resize(1000, 650)
        self.column_names: List[str] = column_names
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Constructs the user interface."""
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
        self.analyze_btn.setObjectName("PrimaryButton")
        self.analyze_btn.clicked.connect(self._handle_analyze)
        footer_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(footer_layout)

        # Results Table (PRD 006 Expansion)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        headers = ['Condition Expression', 'Consistency', 'Coverage', 'RoN', 'Triviality']
        self.table.setHorizontalHeaderLabels(headers)
        
        # Add tooltips for scientific context
        self.table.horizontalHeaderItem(1).setToolTip("Consistency: To what degree is the condition a superset of the outcome? (Goal > 0.9)")
        self.table.horizontalHeaderItem(2).setToolTip("Coverage: To what degree is the outcome a superset of the condition?")
        self.table.horizontalHeaderItem(3).setToolTip("Relevance of Necessity (RoN): Detects triviality. Low RoN with high Consistency indicates a condition present in almost all cases.")
        self.table.horizontalHeaderItem(4).setToolTip("Triviality Proxy (Avg): The average membership score of the condition across all cases.")
        
        layout.addWidget(self.table)

    def _on_add(self) -> None:
        """Adds selected conditions to the test list."""
        selected = self.available_list.selectedItems()
        for item in selected:
            self.test_list.addItem(item.text())

    def _on_add_or(self) -> None:
        """Combines selected conditions into a fuzzy OR expression."""
        selected = [item.text() for item in self.available_list.selectedItems()]
        if len(selected) < 2:
            QMessageBox.information(self, "Info", "Select at least two conditions to create an OR (+) expression.")
            return
        
        expr = " + ".join(selected)
        self.test_list.addItem(expr)

    def _on_remove(self) -> None:
        """Removes selected expressions from the test list."""
        selected = self.test_list.selectedItems()
        for item in selected:
            self.test_list.takeItem(self.test_list.row(item))

    def _handle_analyze(self) -> None:
        """Gathers parameters and emits the analyze_requested signal."""
        conditions = [self.test_list.item(i).text() for i in range(self.test_list.count())]
        outcome = self.outcome_combo.currentText()
        negate_outcome = self.negate_checkbox.isChecked()

        if not conditions or not outcome:
            QMessageBox.warning(self, "Warning", "Please add conditions to test and select an outcome.")
            return

        self.analyze_requested.emit(conditions, outcome, negate_outcome)

    def display_results(self, df: pd.DataFrame) -> None:
        """Populates the results table with consistency, coverage, RoN, and Triviality metrics."""
        self.table.setRowCount(0)
        self.table.setRowCount(len(df))
        
        for row_idx, row in enumerate(df.itertuples(index=False)):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(row.Condition)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(f"{row.Consistency:.6f}"))
            self.table.setItem(row_idx, 2, QTableWidgetItem(f"{row.Coverage:.6f}"))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{row.RoN:.6f}"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(f"{row.Triviality:.6f}"))
            
        self.table.resizeColumnsToContents()
