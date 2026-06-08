from typing import List, Optional, Callable, Dict, Any, Tuple
import numpy as np
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                             QLineEdit, QPushButton, QMessageBox, QHBoxLayout, 
                             QTextEdit, QLabel, QWidget, QFrame)
from PyQt6.QtCore import Qt

class DichotomizationWizard(QDialog):
    """
    Wizard-style dialog for converting continuous or fuzzy-set variables into crisp sets.
    
    Emphasizes 'informed' choices by providing statistical guidance (mean, median)
    and requiring theoretical justification for selected thresholds.
    """

    def __init__(self, parent: Optional[QWidget], column_names: List[str], 
                 get_data_callback: Callable[[str], Optional[np.ndarray]], 
                 on_apply: Callable[[str, float, str, str], None]) -> None:
        """
        Initializes the DichotomizationWizard.

        Args:
            parent: The parent widget.
            column_names: List of available variables in the dataset.
            get_data_callback: Callback to fetch raw data for statistics.
            on_apply: Callback to execute the dichotomization.
        """
        super().__init__(parent)
        self.setWindowTitle("Informed Dichotomization Wizard")
        self.resize(500, 550)
        
        self.column_names: List[str] = column_names
        self.get_data_callback = get_data_callback
        self.on_apply = on_apply
        
        self._setup_ui()
        self._update_statistics()

    def _setup_ui(self) -> None:
        """Constructs the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("Dichotomization Parameters")
        header.setObjectName("HeaderLabel")
        main_layout.addWidget(header)

        # Top Section: Form Layout
        top_section = QWidget()
        form_layout = QFormLayout(top_section)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

        # Source Variable
        self.source_combo = QComboBox()
        self.source_combo.addItems(self.column_names)
        self.source_combo.currentTextChanged.connect(self._handle_source_change)
        form_layout.addRow("Source Variable:", self.source_combo)

        # New Variable Name
        self.new_col_edit = QLineEdit()
        form_layout.addRow("New Crisp Variable:", self.new_col_edit)

        # Threshold Input
        self.threshold_edit = QLineEdit()
        self.threshold_edit.setPlaceholderText("e.g. 0.5")
        form_layout.addRow("Threshold:", self.threshold_edit)

        main_layout.addWidget(top_section)

        # Statistics Section (Styled Frame)
        stats_group = QFrame()
        stats_group.setFrameShape(QFrame.Shape.StyledPanel)
        stats_group.setObjectName("StatsGroup")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        stats_header = QLabel("Distribution Statistics")
        stats_header.setObjectName("SubHeaderLabel")
        stats_layout.addWidget(stats_header)

        self.stats_label = QLabel("Select a variable to see statistics...")
        self.stats_label.setObjectName("MonospaceLabel")
        stats_layout.addWidget(self.stats_label)

        # Quick Thresh Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        self.mean_btn = QPushButton("Use Mean")
        self.mean_btn.clicked.connect(self._use_mean)
        
        self.median_btn = QPushButton("Use Median")
        self.median_btn.clicked.connect(self._use_median)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.mean_btn)
        btn_layout.addWidget(self.median_btn)
        stats_layout.addLayout(btn_layout)

        main_layout.addWidget(stats_group)

        # Justification (Optional)
        main_layout.addWidget(QLabel("Theoretical Justification / Rationale (Optional):"))
        self.rationale_edit = QTextEdit()
        self.rationale_edit.setPlaceholderText("Explain why this threshold represents a qualitative break-point...")
        self.rationale_edit.setMaximumHeight(100)
        main_layout.addWidget(self.rationale_edit)

        # Footer Buttons
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.apply_btn = QPushButton("Create Variable")
        self.apply_btn.setObjectName("SuccessButton")
        self.apply_btn.clicked.connect(self._handle_apply)
        
        footer_layout.addWidget(self.cancel_btn)
        footer_layout.addWidget(self.apply_btn)
        main_layout.addLayout(footer_layout)

    def _handle_source_change(self) -> None:
        """Updates the dialog state when the source variable changes."""
        source_col = self.source_combo.currentText()
        if not source_col:
            return
        
        # Suggest default new name
        self.new_col_edit.setText(f"c_{source_col}")
        self._update_statistics()

    def _update_statistics(self) -> None:
        """Calculates and displays mean/median for the selected variable."""
        source_col = self.source_combo.currentText()
        if not source_col:
            return
            
        data = self.get_data_callback(source_col)
        if data is None or len(data) == 0:
            self.stats_label.setText("No numeric data available.")
            self._current_mean = None
            self._current_median = None
            return
            
        try:
            # Filter NaNs for calculation
            clean_data = data[~np.isnan(data)]
            self._current_mean = np.mean(clean_data)
            self._current_median = np.median(clean_data)
            
            stats_text = (
                f"Mean:   {self._current_mean:.4f}    Min: {np.min(clean_data):.4f}\n"
                f"Median: {self._current_median:.4f}    Max: {np.max(clean_data):.4f}"
            )
            self.stats_label.setText(stats_text)
        except Exception as e:
            self.stats_label.setText(f"Error: {str(e)}")
            self._current_mean = None
            self._current_median = None

    def _use_mean(self) -> None:
        if self._current_mean is not None:
            self.threshold_edit.setText(f"{self._current_mean:.4f}")

    def _use_median(self) -> None:
        if self._current_median is not None:
            self.threshold_edit.setText(f"{self._current_median:.4f}")

    def _handle_apply(self) -> None:
        """Validates input and executes the dichotomization."""
        try:
            source_col = self.source_combo.currentText()
            new_col = self.new_col_edit.text().strip()
            threshold_str = self.threshold_edit.text().strip()
            rationale = self.rationale_edit.toPlainText().strip()
            
            if not new_col:
                raise ValueError("New variable name is required.")
            
            if not threshold_str:
                raise ValueError("Threshold value is required.")
                
            threshold = float(threshold_str)
            
            # Rationale is now optional, as per user request
                
            self.on_apply(source_col, threshold, new_col, rationale)
            self.accept()
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", f"Invalid input: {str(e)}")
