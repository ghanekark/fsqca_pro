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


from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget, 
                             QAbstractItemView, QDialogButtonBox)

class DescriptivesDialog(QDialog):
    def __init__(self, parent, column_names):
        super().__init__(parent)
        self.setWindowTitle("Select Variables for Statistics")
        self.resize(300, 400)
        self.column_names = column_names
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Select Variables:"))
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.list_widget.addItems(self.column_names)
        layout.addWidget(self.list_widget)
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_selected_variables(self):
        return [item.text() for item in self.list_widget.selectedItems()]
