from PyQt6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QPushButton, QFileDialog, QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.lines import Line2D
import numpy as np

class VisualBooleanDialog(QDialog):
    def __init__(self, parent, results, conditions):
        super().__init__(parent)
        self.setWindowTitle("Configuration Chart (Fiss, 2011)")
        self.resize(850, 600)
        
        self.results = results
        self.conditions = conditions
        
        self._setup_ui()
        self._plot_chart()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.solution_combo = QComboBox()
        self.solution_combo.addItems(['Complex', 'Intermediate', 'Parsimonious'])
        self.solution_combo.setCurrentText('Intermediate')
        self.solution_combo.currentIndexChanged.connect(self._update_plot)
        layout.addWidget(self.solution_combo)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.save_btn = QPushButton("Save Chart As...")
        self.save_btn.clicked.connect(self._save_chart)
        layout.addWidget(self.save_btn)

    def _save_chart(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Chart", 
            "", 
            "PNG Image (*.png);;SVG Vector (*.svg);;PDF Document (*.pdf)"
        )
        if filepath:
            try:
                self.figure.savefig(filepath, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "Success", f"Chart successfully saved to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save chart: {str(e)}")

    def _update_plot(self):
        solution_key = self.solution_combo.currentText()
        self._plot_chart(solution_key)

    def _plot_chart(self, solution_key='Intermediate'):
        self.ax.clear()
        
        # Extract terms from the selected solution (list of bitstrings)
        terms = self.results.get(solution_key.lower(), [])
        if not terms:
            self.ax.text(0.5, 0.5, "No solution terms found.", 
                         ha='center', va='center', transform=self.ax.transAxes)
            
            # Clean up axes for empty plot
            for spine in self.ax.spines.values():
                spine.set_visible(False)
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas.draw()
            return

        num_conditions = len(self.conditions)
        num_paths = len(terms)

        # Iterate through each path (X-axis)
        for path_idx, bitstring in enumerate(terms):
            # Iterate through each condition (Y-axis)
            for cond_idx, char in enumerate(bitstring):
                x = path_idx
                y = cond_idx
                
                if char == '1':
                    # Positive: Solid black circle
                    self.ax.scatter(x, y, s=400, facecolor='black', edgecolor='black', zorder=3)
                elif char == '0':
                    # Negated: White circle with black edge
                    self.ax.scatter(x, y, s=400, facecolor='white', edgecolor='black', linewidth=1.5, zorder=3)
                # If '-', do nothing

        # Configure Y-axis
        self.ax.set_yticks(range(num_conditions))
        self.ax.set_yticklabels(self.conditions)
        self.ax.tick_params(axis='y', which='both', left=False, right=False)
        self.ax.invert_yaxis() # Top-to-bottom

        # Configure X-axis
        self.ax.set_xticks(range(num_paths))
        self.ax.set_xticklabels([f"Path {i+1}" for i in range(num_paths)])
        self.ax.tick_params(axis='x', bottom=False, top=False)
        
        # Remove spines (borders)
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        # Set limits to center the circles
        self.ax.set_xlim(-0.5, num_paths - 0.5)
        self.ax.set_ylim(num_conditions - 0.5, -0.5)
        
        # Grid lines for visual guidance
        self.ax.set_yticks(np.arange(-0.5, num_conditions, 1), minor=True)
        self.ax.grid(which='minor', axis='y', linestyle='-', color='lightgray', alpha=0.3)

        # Create custom legend
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Present',
                   markerfacecolor='black', markersize=15),
            Line2D([0], [0], marker='o', color='w', label='Absent',
                   markerfacecolor='white', markeredgecolor='black', markersize=15)
        ]
        self.ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))

        self.figure.tight_layout()
        self.canvas.draw()
