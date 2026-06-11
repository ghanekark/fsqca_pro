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

from typing import Dict, List, Any, Optional
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHBoxLayout, QLabel, QHeaderView, QWidget)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class SolutionContinuumDialog(QDialog):
    """
    Dialog for visualizing the Complexity-Parsimony Continuum in fsQCA.
    
    Provides a side-by-side comparison of Complex, Intermediate, and 
    Parsimonious solutions, highlighting core vs. complementary conditions.
    """

    def __init__(self, parent: Optional[QWidget], results: Dict[str, Any], conditions: List[str]) -> None:
        """
        Initializes the SolutionContinuumDialog.

        Args:
            parent: The parent widget.
            results: Dictionary containing the three solution types ('complex', 'intermediate', 'parsimonious').
            conditions: List of causal condition names used in the analysis.
        """
        super().__init__(parent)
        self.setWindowTitle("Complexity-Parsimony Continuum")
        self.resize(1000, 600)
        
        self.results: Dict[str, Any] = results
        self.conditions: List[str] = conditions
        
        self._setup_ui()
        self._populate_table()

    def _setup_ui(self) -> None:
        """Constructs the user interface components."""
        layout = QVBoxLayout(self)
        
        label = QLabel("Audit of Simplifying Assumptions (Side-by-Side Solution Alignment)")
        label.setObjectName("SubHeaderLabel")
        layout.addWidget(label)
        
        description = QLabel(
            "This view aligns causal paths from the three solution types. "
            "Bold terms in the Intermediate solution indicate 'Core' conditions (those present in the Parsimonious solution)."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Path Index", "Complex Solution", "Intermediate Solution", "Parsimonious Solution"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def _get_path_string(self, term: str) -> str:
        """
        Converts a binary/trinary term string to a human-readable causal path.

        Args:
            term: The term string (e.g., '10-').

        Returns:
            The causal path string (e.g., 'A * ~B').
        """
        parts = []
        for i, char in enumerate(term):
            if char == '1':
                parts.append(self.conditions[i])
            elif char == '0':
                parts.append(f"~{self.conditions[i]}")
        return " * ".join(parts) if parts else "1"

    def _covers(self, pi: str, term: str) -> bool:
        """
        Checks if a prime implicant covers a more specific term.

        Args:
            pi: The prime implicant (e.g., '1--').
            term: The term to check (e.g., '101').

        Returns:
            True if pi covers term, False otherwise.
        """
        for i in range(len(pi)):
            if pi[i] != '-' and pi[i] != term[i]:
                return False
        return True

    def _format_intermediate_with_core(self, intermediate_term: str, parsimonious_term: str) -> str:
        """
        Formats an intermediate path string with HTML bolding for core conditions.

        Args:
            intermediate_term: The intermediate solution term.
            parsimonious_term: The parsimonious solution term that covers it.

        Returns:
            An HTML-formatted string of the intermediate path.
        """
        parts = []
        for i, char in enumerate(intermediate_term):
            if char == '-':
                continue
            
            condition_str = self.conditions[i] if char == '1' else f"~{self.conditions[i]}"
            
            # If the parsimonious term also has this literal, it's a 'core' condition
            if parsimonious_term[i] == char:
                parts.append(f"<b>{condition_str}</b>")
            else:
                parts.append(condition_str)
        
        return " * ".join(parts)

    def _populate_table(self) -> None:
        """Aligns the three solution types and populates the results table."""
        complex_sol: List[str] = self.results.get('complex', [])
        intermediate_sol: List[str] = self.results.get('intermediate', [])
        parsimonious_sol: List[str] = self.results.get('parsimonious', [])
        
        # We align by Intermediate terms as the primary reference
        rows: List[Dict[str, str]] = []
        
        for i, int_term in enumerate(intermediate_sol):
            # 1. Find the parsimonious term that covers this intermediate term
            p_term = next((p for p in parsimonious_sol if self._covers(p, int_term)), "---")
            
            # 2. Find all complex terms covered by this intermediate term
            c_terms = [c for c in complex_sol if self._covers(int_term, c)]
            
            if not c_terms:
                rows.append({
                    'index': f"{i+1}",
                    'complex': "---",
                    'intermediate': self._get_path_string(int_term),
                    'intermediate_rich': self._format_intermediate_with_core(int_term, p_term) if p_term != "---" else self._get_path_string(int_term),
                    'parsimonious': self._get_path_string(p_term) if p_term != "---" else "---"
                })
            else:
                for j, c_term in enumerate(c_terms):
                    rows.append({
                        'index': f"{i+1}.{j+1}" if len(c_terms) > 1 else f"{i+1}",
                        'complex': self._get_path_string(c_term),
                        'intermediate': self._get_path_string(int_term),
                        'intermediate_rich': self._format_intermediate_with_core(int_term, p_term) if p_term != "---" else self._get_path_string(int_term),
                        'parsimonious': self._get_path_string(p_term) if p_term != "---" else "---"
                    })

        self.table.setRowCount(len(rows))
        for r_idx, row in enumerate(rows):
            # Index
            self.table.setItem(r_idx, 0, QTableWidgetItem(row['index']))
            
            # Complex
            self.table.setItem(r_idx, 1, QTableWidgetItem(row['complex']))
            
            # Intermediate (with rich text for bolding core conditions)
            int_item = QLabel(row['intermediate_rich'])
            int_item.setContentsMargins(5, 0, 5, 0)
            int_item.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setCellWidget(r_idx, 2, int_item)
            
            # Parsimonious
            self.table.setItem(r_idx, 3, QTableWidgetItem(row['parsimonious']))

        self.table.resizeRowsToContents()
