import tkinter as tk
from tkinter import ttk

class DescriptivesDialog(tk.Toplevel):
    def __init__(self, parent, column_names, on_calculate):
        super().__init__(parent)
        self.title("Descriptive Statistics")
        self.column_names = column_names
        self.on_calculate = on_calculate
        
        self.geometry("600x400")
        self.minsize(400, 300)
        self.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        # Left side: Variable Selection
        left_frame = ttk.Frame(self, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(left_frame, text="Select Variables:").pack(anchor=tk.W)
        
        self.listbox = tk.Listbox(left_frame, selectmode='extended')
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        for col in self.column_names:
            self.listbox.insert(tk.END, col)

        self.calc_btn = ttk.Button(left_frame, text="Calculate", command=self._handle_calculate)
        self.calc_btn.pack(fill=tk.X, pady=5)

        # Right side: Results
        right_frame = ttk.Frame(self, padding="10")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(right_frame, text="Results:").pack(anchor=tk.W)
        
        self.text_result = tk.Text(right_frame, font=("Courier", 10))
        self.text_result.pack(fill=tk.BOTH, expand=True, pady=5)

    def _handle_calculate(self):
        selected_indices = self.listbox.curselection()
        selected_cols = [self.listbox.get(i) for i in selected_indices]
        
        if not selected_cols:
            self.text_result.delete("1.0", tk.END)
            self.text_result.insert(tk.END, "Please select at least one variable.")
            return

        result = self.on_calculate(selected_cols)
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, result)
