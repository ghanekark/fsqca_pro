import sys
from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQCA - Qualitative Comparative Analysis")
        self.resize(1024, 768)
        
        self._setup_menu()
        self._setup_ui()

    def _setup_menu(self):
        menubar = self.menuBar()
        
        # File Menu
        self.file_menu = menubar.addMenu("File")
        
        self.action_open = QAction("Open Data...", self)
        self.file_menu.addAction(self.action_open)
        
        self.action_save = QAction("Save Data As...", self)
        self.file_menu.addAction(self.action_save)
        
        self.file_menu.addSeparator()
        
        self.action_exit = QAction("Exit", self)
        self.file_menu.addAction(self.action_exit)
        
        # Edit Menu
        self.edit_menu = menubar.addMenu("Edit")
        
        # Variables Menu
        self.variables_menu = menubar.addMenu("Variables")
        
        self.action_compute = QAction("Compute Variable...", self)
        self.variables_menu.addAction(self.action_compute)
        
        # Analyze Menu
        self.analyze_menu = menubar.addMenu("Analyze")
        
        self.action_calibrate = QAction("Calibrate...", self)
        self.analyze_menu.addAction(self.action_calibrate)
        
        self.action_truth_table = QAction("Truth Table Algorithm...", self)
        self.analyze_menu.addAction(self.action_truth_table)
        
        self.action_necessity = QAction("Necessary Conditions...", self)
        self.analyze_menu.addAction(self.action_necessity)
        
        self.action_standard_analysis = QAction("Standard Analysis...", self)
        self.analyze_menu.addAction(self.action_standard_analysis)

        self.action_sensitivity = QAction("Sensitivity Analysis...", self)
        self.analyze_menu.addAction(self.action_sensitivity)

    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        self.table = QTableWidget()
        layout.addWidget(self.table)

    def populate_grid(self, dataframe):
        """
        Clears the table and populates it with data from a pandas DataFrame.
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
        
        # Populate rows
        for row_idx, row in enumerate(dataframe.itertuples(index=False)):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)
        
        self.table.resizeColumnsToContents()
