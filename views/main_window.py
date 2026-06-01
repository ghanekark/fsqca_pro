import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, 
                             QVBoxLayout, QWidget, QSplitter, QTextEdit)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("fsqca_pro")
        self.resize(1024, 768)
        
        self._setup_menu()
        self._setup_ui()

    def _setup_menu(self):
        menubar = self.menuBar()
        
        # --- File Menu ---
        self.file_menu = menubar.addMenu("&File")
        
        self.action_file_new = QAction("New", self)
        self.file_menu.addAction(self.action_file_new)
        
        self.action_file_new_expr = QAction("New from Expression...", self)
        self.file_menu.addAction(self.action_file_new_expr)
        
        self.action_file_open = QAction("Open...", self)
        self.file_menu.addAction(self.action_file_open)
        
        self.action_file_save = QAction("Save", self)
        self.file_menu.addAction(self.action_file_save)
        
        self.action_file_save_as = QAction("Save As...", self)
        self.file_menu.addAction(self.action_file_save_as)
        
        self.file_menu.addSeparator()
        
        self.action_file_print_res = QAction("Print Results...", self)
        self.file_menu.addAction(self.action_file_print_res)
        
        self.action_file_save_res = QAction("Save Results...", self)
        self.file_menu.addAction(self.action_file_save_res)
        
        self.action_file_export_log = QAction("Export Research Log...", self)
        self.file_menu.addAction(self.action_file_export_log)
        
        self.file_menu.addSeparator()
        
        self.action_file_quit = QAction("Quit", self)
        self.file_menu.addAction(self.action_file_quit)
        
        # --- Variables Menu ---
        self.vars_menu = menubar.addMenu("&Variables")
        
        self.action_vars_add = QAction("Add", self)
        self.vars_menu.addAction(self.action_vars_add)
        
        self.action_vars_delete = QAction("Delete", self)
        self.vars_menu.addAction(self.action_vars_delete)
        
        self.action_vars_compute = QAction("Compute...", self)
        self.vars_menu.addAction(self.action_vars_compute)
        
        self.action_vars_recode = QAction("Recode...", self)
        self.vars_menu.addAction(self.action_vars_recode)

        self.action_vars_dichotomize = QAction("Dichotomize...", self)
        self.vars_menu.addAction(self.action_vars_dichotomize)

        self.action_vars_calibrate = QAction("Calibration...", self)
        self.vars_menu.addAction(self.action_vars_calibrate)
        
        # --- Cases Menu ---
        self.cases_menu = menubar.addMenu("&Cases")
        
        self.action_cases_add = QAction("Add", self)
        self.cases_menu.addAction(self.action_cases_add)
        
        self.action_cases_delete = QAction("Delete", self)
        self.cases_menu.addAction(self.action_cases_delete)
        
        self.action_cases_select_if = QAction("Select If...", self)
        self.cases_menu.addAction(self.action_cases_select_if)
        
        self.action_cases_cancel_sel = QAction("Cancel Selection", self)
        self.cases_menu.addAction(self.action_cases_cancel_sel)
        
        # --- Analyze Menu ---
        self.analyze_menu = menubar.addMenu("&Analyze")
        
        self.action_analyze_tt = QAction("Truth Table Algorithm...", self)
        self.analyze_menu.addAction(self.action_analyze_tt)
        
        self.action_analyze_induction = QAction("Analytic Induction...", self)
        self.analyze_menu.addAction(self.action_analyze_induction)
        
        self.action_analyze_necessity = QAction("Necessary Conditions...", self)
        self.analyze_menu.addAction(self.action_analyze_necessity)
        
        self.action_analyze_coincidence = QAction("Set Coincidence...", self)
        self.analyze_menu.addAction(self.action_analyze_coincidence)
        
        self.action_analyze_subset = QAction("Subset/Superset Analysis...", self)
        self.analyze_menu.addAction(self.action_analyze_subset)

        self.action_analyze_sensitivity = QAction("Sensitivity Analysis...", self)
        self.analyze_menu.addAction(self.action_analyze_sensitivity)
        
        # Statistics Sub-menu
        self.stats_menu = self.analyze_menu.addMenu("Statistics")
        self.action_stats_descriptives = QAction("Descriptives...", self)
        self.stats_menu.addAction(self.action_stats_descriptives)
        
        # --- View Menu ---
        self.view_menu = menubar.addMenu("&View")
        self.action_view_dark_mode = QAction("Dark Mode", self)
        self.action_view_dark_mode.setCheckable(True)
        self.view_menu.addAction(self.action_view_dark_mode)
        
        # --- Graphs Menu ---
        self.graphs_menu = menubar.addMenu("&Graphs")
        
        self.action_graphs_xy = QAction("XY Plot...", self)
        self.graphs_menu.addAction(self.action_graphs_xy)

    def _setup_ui(self):
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.setCentralWidget(self.splitter)
        
        # Top half: Data Grid
        self.table = QTableWidget()
        self.splitter.addWidget(self.table)
        
        # Bottom half: Results Log
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        # Use a monospace font for better alignment of results
        mono_font = QFont("Courier New", 10)
        mono_font.setStyleHint(QFont.StyleHint.Monospace)
        self.log_console.setFont(mono_font)
        self.splitter.addWidget(self.log_console)
        
        # Initial sizes: prioritize the table
        self.splitter.setSizes([500, 250])

    def populate_grid(self, dataframe: pd.DataFrame, calibration_metadata: Dict[str, Any] = None) -> None:
        """
        Clears the table and populates it with data from a pandas DataFrame.
        Sets tooltips on headers for variables with calibration metadata.
        """
        self.table.clear()
        
        if dataframe is None:
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # Set dimensions
        self.table.setColumnCount(len(dataframe.columns))
        self.table.setRowCount(len(dataframe))
        
        # Set headers
        self.table.setHorizontalHeaderLabels(dataframe.columns)

        # Set Tooltips for Metadata (PRD 004 Audit View)
        for i, col in enumerate(dataframe.columns):
            if calibration_metadata and col in calibration_metadata:
                meta = calibration_metadata[col]
                anchors = meta.get('anchors', {})
                tooltip = (
                    f"Variable: {col}\n"
                    f"Source: {meta.get('source', 'N/A')}\n"
                    f"--- Anchors ---\n"
                    f"Full (1.0): {anchors.get('full', 'N/A')}\n"
                    f"Cross (0.5): {anchors.get('cross', 'N/A')}\n"
                    f"Non (0.0): {anchors.get('non', 'N/A')}\n"
                    f"--- Rationale ---\n"
                    f"{meta.get('rationale', 'No rationale provided.')}"
                )
                header_item = self.table.horizontalHeaderItem(i)
                if header_item:
                    header_item.setToolTip(tooltip)
        
        # Populate rows
        for row_idx, row in enumerate(dataframe.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                # Handle numeric formatting for readability
                if isinstance(value, (float, np.float64)):
                    item = QTableWidgetItem(f"{value:.4f}")
                else:
                    item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)
        
        self.table.resizeColumnsToContents()
