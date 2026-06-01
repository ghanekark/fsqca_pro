import os
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.abspath(os.getcwd()))

from utils.logger import ResearchLogger
from models.data_model import QCADataModel

def test_replicability_logger():
    print("Starting Replicability Logger Test...")
    
    # 1. Initialize Logger and Model
    logger = ResearchLogger()
    logger.clear_log()
    model = QCADataModel()
    
    # 2. Simulate some data actions
    print("Simulating analytical actions...")
    
    # Create dummy data
    df = pd.DataFrame({
        'A': [10, 20, 30, 40, 50],
        'B': [0.1, 0.4, 0.6, 0.8, 0.9],
        'OUT': [0, 0, 1, 1, 1]
    })
    model.dataframe = df
    
    # Action 1: Calibration
    success, msg = model.calibrate_variable('A', 'A_fuzzy', 45, 25, 15, rationale="Standard thresholds for A.")
    print(f"Calibration: {success}, {msg}")
    
    # Action 2: Dichotomization
    success, msg = model.dichotomize_variable('B', 0.5, 'B_crisp', rationale="Median split for B.")
    print(f"Dichotomization: {success}, {msg}")
    
    # Action 3: Manual Variable Creation (Simulated from Controller)
    logger.log_action(
        category="VARIABLE_CREATION",
        description="Manually added a new variable named 'NewVar'."
    )
    
    # 3. Export the log (MD)
    export_path_md = "test_research_log.md"
    success_md = logger.export_log(export_path_md)
    
    # 4. Export the log (TXT)
    export_path_txt = "test_research_log.txt"
    success_txt = logger.export_log(export_path_txt)
    
    if success_md and os.path.exists(export_path_md) and success_txt and os.path.exists(export_path_txt):
        print(f"Logs successfully exported to {export_path_md} and {export_path_txt}")
        
        # Validate TXT content
        with open(export_path_txt, 'r') as f:
            content = f.read()
            assert "[CALIBRATION]" in content
            assert "[DICHOTOMIZATION]" in content
            print("Test PASSED: TXT export verified.")
    else:
        print("Test FAILED: Log export failed.")

if __name__ == "__main__":
    test_replicability_logger()
