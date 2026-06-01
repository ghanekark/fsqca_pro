from typing import List, Optional, Callable, Dict, Any, Tuple
import numpy as np
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                             QLineEdit, QPushButton, QMessageBox, QHBoxLayout, 
                             QTextEdit, QLabel, QWidget)
from PyQt6.QtCore import Qt

# Try to import matplotlib for visualization
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

class CalibrationDialog(QDialog):
    """
    Dialog for 'Direct Method' calibration of raw variables into fuzzy sets.
    
    Provides interactive visualization and documentation of qualitative anchors.
    Supports both manual (direct) and automated (batch) calibration workflows.
    """

    def __init__(self, parent: Optional[QWidget], column_names: List[str], 
                 get_data_callback: Callable[[str], Optional[np.ndarray]], 
                 on_apply: Callable[[str, str, float, float, float, str], None], 
                 auto_calc_callback: Callable[[str], Optional[Tuple[float, float, float]]], 
                 batch_calc_callback: Callable[[], None]) -> None:
        """
        Initializes the CalibrationDialog.

        Args:
            parent: The parent widget.
            column_names: List of available variables in the dataset.
            get_data_callback: Callback to fetch raw data for plotting.
            on_apply: Callback to execute a single manual calibration.
            auto_calc_callback: Callback to suggest anchors for a variable.
            batch_calc_callback: Callback to trigger batch auto-calibration.
        """
        super().__init__(parent)
        self.setWindowTitle("Direct Method Calibration")
        self.resize(900, 550)
        
        self.column_names: List[str] = column_names
        self.get_data_callback = get_data_callback
        self.on_apply = on_apply
        self.auto_calc_callback = auto_calc_callback
        self.batch_calc_callback = batch_calc_callback
        
        self._setup_ui()
        self._update_plot()

    def _setup_ui(self) -> None:
        """Constructs the user interface."""
        main_layout = QHBoxLayout(self)
        
        # --- Left Panel: Inputs ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        form_layout = QFormLayout()

        # Source Column
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.column_names)
        self.source_combo.currentTextChanged.connect(self._handle_source_change)
        
        source_row = QHBoxLayout()
        source_row.addWidget(self.source_combo)
        
        self.auto_btn = QPushButton("Suggest")
        self.auto_btn.setToolTip("Suggest anchors based on 95th, 50th, and 5th percentiles")
        self.auto_btn.clicked.connect(self._handle_auto_calc)
        source_row.addWidget(self.auto_btn)
        
        form_layout.addRow("Source Variable:", source_row)

        # New Column Name
        self.new_col_edit = QLineEdit()
        form_layout.addRow("Calibrated Name:", self.new_col_edit)

        # Thresholds
        self.p_full_edit = QLineEdit()
        self.p_full_edit.textChanged.connect(self._update_plot_lines)
        form_layout.addRow("Full Membership (1.0):", self.p_full_edit)

        self.p_cross_edit = QLineEdit()
        self.p_cross_edit.textChanged.connect(self._update_plot_lines)
        form_layout.addRow("Crossover Point (0.5):", self.p_cross_edit)

        self.p_non_edit = QLineEdit()
        self.p_non_edit.textChanged.connect(self._update_plot_lines)
        form_layout.addRow("Full Non-membership (0.0):", self.p_non_edit)

        left_layout.addLayout(form_layout)

        # Rationale (PRD 004 Audit)
        left_layout.addWidget(QLabel("Theoretical Justification / Rationale:"))
        self.rationale_edit = QTextEdit()
        self.rationale_edit.setPlaceholderText("Explain why these anchors were chosen based on theoretical knowledge...")
        left_layout.addWidget(self.rationale_edit)

        # Apply Button (Manual)
        self.apply_btn = QPushButton("Calibrate")
        self.apply_btn.setObjectName("SuccessButton")
        self.apply_btn.clicked.connect(self._handle_apply)
        left_layout.addWidget(self.apply_btn)
        
        left_layout.addSpacing(15)
        
        # Batch Auto-Calibration Button (PRD 007)
        self.batch_btn = QPushButton("Batch Auto-Calibrate All Numeric")
        self.batch_btn.setObjectName("PrimaryButton")
        self.batch_btn.clicked.connect(self._handle_batch)
        left_layout.addWidget(self.batch_btn)
        
        main_layout.addWidget(left_widget, 1)

        # --- Right Panel: Visualization ---
        if HAS_MATPLOTLIB:
            self.canvas_widget = QWidget()
            canvas_layout = QVBoxLayout(self.canvas_widget)
            
            self.figure = Figure(figsize=(5, 4), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            canvas_layout.addWidget(self.canvas)
            
            self.ax = self.figure.add_subplot(111)
            main_layout.addWidget(self.canvas_widget, 2)
        else:
            main_layout.addWidget(QLabel("Matplotlib not found. Visualization unavailable."), 2)

    def _handle_source_change(self) -> None:
        """Updates the dialog state when the source variable changes."""
        source_col = self.source_combo.currentText()
        if not source_col:
            return
        
        # Suggest default new name
        self.new_col_edit.setText(f"f_{source_col}")
        self._update_plot()

    def _handle_auto_calc(self) -> None:
        """Triggers the percentile suggestion for the current variable."""
        source_col = self.source_combo.currentText()
        if not source_col:
            return
            
        thresholds = self.auto_calc_callback(source_col)
        if thresholds:
            p_full, p_cross, p_non = thresholds
            
            # Auto-populate the calibrated name (PRD 002 Suggestion enhancement)
            self.new_col_edit.setText(f"f_{source_col}")
            
            self.p_full_edit.setText(f"{p_full:.4f}")
            self.p_cross_edit.setText(f"{p_cross:.4f}")
            self.p_non_edit.setText(f"{p_non:.4f}")
            self._update_plot()
        else:
            QMessageBox.warning(self, "Warning", "Could not calculate suggestions for this column.")

    def _update_plot(self) -> None:
        """Redraws the distribution histogram for the selected variable."""
        if not HAS_MATPLOTLIB:
            return
            
        source_col = self.source_combo.currentText()
        if not source_col:
            return
            
        data = self.get_data_callback(source_col)
        if data is None or len(data) == 0:
            return
            
        self.ax.clear()
        self.ax.hist(data, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
        self.ax.set_title(f"Distribution of {source_col}")
        self.ax.set_xlabel("Value")
        self.ax.set_ylabel("Frequency")
        
        self._update_plot_lines()

    def _update_plot_lines(self) -> None:
        """Updates the anchor markers on the histogram without redrawing the data."""
        if not HAS_MATPLOTLIB:
            return
            
        # Remove previous lines/texts
        for line in self.ax.get_lines() + self.ax.texts:
            line.remove()
            
        try:
            p_full = float(self.p_full_edit.text())
            self.ax.axvline(p_full, color='green', linestyle='--', label='Full')
            self.ax.text(p_full, self.ax.get_ylim()[1]*0.9, ' 1.0', color='green')
        except ValueError: pass
        
        try:
            p_cross = float(self.p_cross_edit.text())
            self.ax.axvline(p_cross, color='red', linestyle='-', label='Cross')
            self.ax.text(p_cross, self.ax.get_ylim()[1]*0.9, ' 0.5', color='red')
        except ValueError: pass
        
        try:
            p_non = float(self.p_non_edit.text())
            self.ax.axvline(p_non, color='blue', linestyle='--', label='Non')
            self.ax.text(p_non, self.ax.get_ylim()[1]*0.9, ' 0.0', color='blue')
        except ValueError: pass
        
        self.canvas.draw()

    def _handle_apply(self) -> None:
        """Validates input and executes a manual calibration."""
        try:
            source_col = self.source_combo.currentText()
            new_col = self.new_col_edit.text().strip()
            p_full = float(self.p_full_edit.text())
            p_cross = float(self.p_cross_edit.text())
            p_non = float(self.p_non_edit.text())
            rationale = self.rationale_edit.toPlainText().strip()
            
            if not new_col:
                raise ValueError("New column name is required.")
            
            # Substantive validation
            if p_full == p_cross or p_non == p_cross:
                raise ValueError("Crossover point cannot be equal to Full or Non-membership anchors.")
                
            self.on_apply(source_col, new_col, p_full, p_cross, p_non, rationale)
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid input: {str(e)}")

    def _handle_batch(self) -> None:
        """Prompts confirmation and executes batch auto-calibration."""
        reply = QMessageBox.question(
            self, "Confirm Batch Calibration",
            "This will automatically calibrate all numeric columns (using 95th/50th/5th percentiles) that haven't been calibrated yet. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.batch_calc_callback()
            self.accept()
