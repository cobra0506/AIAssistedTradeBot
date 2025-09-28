import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Import the indicators library
from simple_strategy.strategies.indicators_library import ema

def debug_ema_on_macd():
    """Debug EMA function specifically on MACD line data"""
    print("="*60)
    print("DEBUGGING EMA ON MACD LINE")
    print("="*60)
    
    # Create MACD line data (from our previous debug)
    macd_line_data = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 
                      2.386419753086429, 2.424279835390962, 1.9949744357151928, 
                      1.336870009485068, 0.745366382481663, 0.6805846233597208, 
                      0.9070318684835144, 1.2786072222793194, 1.7068236442116103, 
                      1.6854372292527842, 1.8746545041690155]
    
    macd_series = pd.Series(macd_line_data)
    signal_period = 3
    
    print(f"MACD line data: {macd_series.tolist()}")
    print(f"Signal period: {signal_period}")
    
    # Calculate signal line (EMA of MACD line)
    signal_line = ema(macd_series, signal_period)
    
    print(f"\nSignal line result: {signal_line.tolist()}")
    print(f"Non-NaN values: {signal_line.notna().sum()}")
    
    # Let's manually calculate what the signal line should be
    print("\nManual calculation:")
    
    # Find the first 3 non-NaN values in MACD line
    non_nan_indices = []
    non_nan_values = []
    for i, val in enumerate(macd_series):
        if not pd.isna(val):
            non_nan_indices.append(i)
            non_nan_values.append(val)
            if len(non_nan_values) >= 3:
                break
    
    print(f"First 3 non-NaN MACD values: {non_nan_values}")
    print(f"Their indices: {non_nan_indices}")
    
    if len(non_nan_values) >= 3:
        # Calculate first signal value (SMA of first 3 non-NaN MACD values)
        first_signal = sum(non_nan_values) / len(non_nan_values)
        print(f"First signal value (SMA): {first_signal}")
        
        # Calculate smoothing factor
        smoothing = 2 / (signal_period + 1)
        print(f"Smoothing factor: {smoothing}")
        
        # Calculate expected signal values
        expected_signal = [np.nan] * len(macd_series)
        expected_signal[non_nan_indices[-1]] = first_signal
        
        for i in range(non_nan_indices[-1] + 1, len(macd_series)):
            if not pd.isna(macd_series.iloc[i]):
                expected_signal[i] = smoothing * macd_series.iloc[i] + (1 - smoothing) * expected_signal[i-1]
        
        print(f"Expected signal line: {[f'{x:.4f}' if not pd.isna(x) else 'nan' for x in expected_signal]}")
        
        # Compare with actual result
        print("\nComparison:")
        for i in range(len(signal_line)):
            if pd.isna(signal_line.iloc[i]) and pd.isna(expected_signal[i]):
                print(f"✓ Index {i}: Both are NaN")
            elif not pd.isna(signal_line.iloc[i]) and not pd.isna(expected_signal[i]):
                if abs(signal_line.iloc[i] - expected_signal[i]) < 0.0001:
                    print(f"✓ Index {i}: {signal_line.iloc[i]:.4f} == {expected_signal[i]:.4f}")
                else:
                    print(f"✗ Index {i}: {signal_line.iloc[i]:.4f} != {expected_signal[i]:.4f}")
            else:
                print(f"✗ Index {i}: One is NaN, the other isn't")
    
    # Let's also test the EMA function with a simple series
    print("\n" + "="*60)
    print("TESTING EMA WITH SIMPLE SERIES")
    print("="*60)
    
    simple_series = pd.Series([1, 2, 3, 4, 5])
    simple_ema = ema(simple_series, 3)
    print(f"Simple series: {simple_series.tolist()}")
    print(f"Simple EMA (period 3): {simple_ema.tolist()}")
    print(f"Expected: [nan, nan, 2.0, 3.0, 4.0]")

if __name__ == "__main__":
    debug_ema_on_macd()