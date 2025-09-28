import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from simple_strategy.strategies.indicators_library import ema
import pandas as pd

# Test the updated EMA function
test_data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
result = ema(test_data, 3)
print("EMA result:", result.tolist())
print("Expected: [nan, nan, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]")