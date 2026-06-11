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

from typing import List, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTextEdit, QPushButton, 
                             QLabel, QHBoxLayout, QWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class SanitizationReportDialog(QDialog):
    """
    Dialog for displaying a transparency report after data ingestion.
    
    Lists all automated actions taken (renaming, conversion, row dropping)
    and the methodological rationale behind each.
    """

    def __init__(self, parent: Optional[QWidget], log_entries: List[str]) -> None:
        """
        Initializes the SanitizationReportDialog.

        Args:
            parent: The parent widget.
            log_entries: List of strings describing sanitization actions.
        """
        super().__init__(parent)
        self.setWindowTitle("Data Ingestion & Sanitization Report")
        self.resize(700, 450)
        
        self.log_entries = log_entries
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Constructs the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Scientific Transparency Report: Data Ingestion")
        header.setObjectName("SubHeaderLabel")
        layout.addWidget(header)
        
        description = QLabel(
            "The following automated actions were taken to ensure your dataset is compatible "
            "with set-theoretic Boolean algorithms while maintaining methodological rigor."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Log Display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Courier New", 10))
        
        # Format the log for readability
        if not self.log_entries:
            report_text = "No sanitization actions were required. Data loaded as-is."
        else:
            report_text = ""
            for i, entry in enumerate(self.log_entries, 1):
                report_text += f"[{i}] {entry}\n\n"
        
        self.text_edit.setPlainText(report_text)
        layout.addWidget(self.text_edit)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("Acknowledge")
        ok_btn.setObjectName("SuccessButton")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
