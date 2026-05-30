from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QComboBox, 
                             QPushButton, QLabel, QScrollArea, QWidget)

class AssumptionsDialog(QDialog):
    def __init__(self, parent, condition_names, submit_callback):
        super().__init__(parent)
        self.setWindowTitle("Directional Expectations")
        self.resize(400, 450)
        self.condition_names = condition_names
        self.submit_callback = submit_callback
        self.combos = {}
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Specify directional expectations for intermediate solutions:"))
        
        # Scroll Area for conditions (useful if there are many)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        
        form_layout = QFormLayout(scroll_widget)
        
        options = ["Present", "Absent", "Present or Absent"]
        
        for cond in self.condition_names:
            combo = QComboBox()
            combo.addItems(options)
            combo.setCurrentText("Present or Absent")
            form_layout.addRow(QLabel(f"{cond}:"), combo)
            self.combos[cond] = combo
            
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # OK Button
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._on_ok)
        layout.addWidget(self.ok_btn)

    def _on_ok(self):
        results = {cond: combo.currentText() for cond, combo in self.combos.items()}
        self.submit_callback(results)
        self.accept()
