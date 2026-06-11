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

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class XYPlotDialog(tk.Toplevel):
    def __init__(self, parent, dataframe):
        super().__init__(parent)
        self.title("XY Plot (Fuzzy-Set Subset Relations)")
        self.dataframe = dataframe
        self.column_names = list(dataframe.columns)
        
        self.geometry("700x600")
        self.minsize(600, 500)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        # Control Frame (Top)
        ctrl_frame = ttk.Frame(self, padding="10")
        ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl_frame, text="X-Axis:").grid(row=0, column=0, padx=5)
        self.x_combo = ttk.Combobox(ctrl_frame, values=self.column_names, state="readonly")
        self.x_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(ctrl_frame, text="Y-Axis:").grid(row=0, column=2, padx=5)
        self.y_combo = ttk.Combobox(ctrl_frame, values=self.column_names, state="readonly")
        self.y_combo.grid(row=0, column=3, padx=5)

        self.plot_btn = ttk.Button(ctrl_frame, text="Generate Plot", command=self._handle_plot)
        self.plot_btn.grid(row=0, column=4, padx=10)

        # Plot Frame (Bottom)
        self.plot_frame = ttk.Frame(self, padding="10")
        self.plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Initial empty figure
        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _handle_plot(self):
        x_col = self.x_combo.get()
        y_col = self.y_combo.get()

        if not x_col or not y_col:
            return

        # Clear existing plot
        self.ax.clear()

        # Data
        x_data = self.dataframe[x_col]
        y_data = self.dataframe[y_col]

        # Scatter plot
        self.ax.scatter(x_data, y_data, alpha=0.6, color='blue', edgecolors='k')
        
        # Labels
        self.ax.set_xlabel(x_col)
        self.ax.set_ylabel(y_col)
        self.ax.set_title(f"{y_col} by {x_col}")

        # Ensure consistent fuzzy-set scale (0 to 1) if possible, or auto-scale
        # But we definitely need the diagonal line
        min_val = min(x_data.min(), y_data.min(), 0)
        max_val = max(x_data.max(), y_data.max(), 1)
        
        # Diagonal line (y=x)
        self.ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='y=x (Identity)')
        
        self.ax.set_xlim(min_val - 0.05, max_val + 0.05)
        self.ax.set_ylim(min_val - 0.05, max_val + 0.05)
        self.ax.grid(True, linestyle=':', alpha=0.6)
        self.ax.legend()

        self.canvas.draw()
