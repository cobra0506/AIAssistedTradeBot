import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Import the indicators library
from simple_strategy.strategies.indicators_library import macd, ema

def debug_ema():
    """Debug the EMA function"""
    print("="*60)
    print("DEBUGGING EMA FUNCTION")
    print("="*60)
    
    # Simple test data
    test_data = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    period = 3
    
    # Calculate EMA
    result = ema(test_data, period)
    
    print(f"Test data: {test_data.tolist()}")
    print(f"Period: {period}")
    print(f"EMA result: {result.tolist()}")
    print(f"Expected: [nan, nan, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]")
    
    # Check if EMA is working correctly
    expected = [np.nan, np.nan, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    for i in range(len(result)):
        if pd.isna(result.iloc[i]) and pd.isna(expected[i]):
            print(f"✓ Index {i}: Both are NaN")
        elif not pd.isna(result.iloc[i]) and not pd.isna(expected[i]):
            if abs(result.iloc[i] - expected[i]) < 0.0001:
                print(f"✓ Index {i}: {result.iloc[i]} == {expected[i]}")
            else:
                print(f"✗ Index {i}: {result.iloc[i]} != {expected[i]}")
        else:
            print(f"✗ Index {i}: One is NaN, the other isn't")

def debug_macd():
    """Debug the MACD function step by step"""
    print("\n" + "="*60)
    print("DEBUGGING MACD FUNCTION")
    print("="*60)
    
    # Simple test data
    test_data = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                          110, 108, 106, 105, 107, 109, 111, 113, 112, 114])
    
    # MACD parameters
    fast_period = 5
    slow_period = 10
    signal_period = 3
    
    print(f"Test data: {test_data.tolist()}")
    print(f"Parameters: fast={fast_period}, slow={slow_period}, signal={signal_period}")
    
    # Step 1: Calculate fast EMA
    ema_fast = ema(test_data, fast_period)
    print(f"\nStep 1 - Fast EMA ({fast_period}):")
    print(f"Result: {ema_fast.tolist()}")
    print(f"Non-NaN values: {ema_fast.notna().sum()}")
    
    # Step 2: Calculate slow EMA
    ema_slow = ema(test_data, slow_period)
    print(f"\nStep 2 - Slow EMA ({slow_period}):")
    print(f"Result: {ema_slow.tolist()}")
    print(f"Non-NaN values: {ema_slow.notna().sum()}")
    
    # Step 3: Calculate MACD line
    macd_line = ema_fast - ema_slow
    print(f"\nStep 3 - MACD line (Fast EMA - Slow EMA):")
    print(f"Result: {macd_line.tolist()}")
    print(f"Non-NaN values: {macd_line.notna().sum()}")
    
    # Step 4: Calculate signal line
    signal_line = ema(macd_line, signal_period)
    print(f"\nStep 4 - Signal line (EMA of MACD line, {signal_period}):")
    print(f"Result: {signal_line.tolist()}")
    print(f"Non-NaN values: {signal_line.notna().sum()}")
    
    # Step 5: Calculate histogram
    histogram = macd_line - signal_line
    print(f"\nStep 5 - Histogram (MACD line - Signal line):")
    print(f"Result: {histogram.tolist()}")
    print(f"Non-NaN values: {histogram.notna().sum()}")
    
    # Step 6: Calculate MACD using the MACD function
    print(f"\nStep 6 - Using MACD function directly:")
    macd_func_line, signal_func_line, histogram_func = macd(test_data, fast_period, slow_period, signal_period)
    
    print(f"MACD line: {macd_func_line.tolist()}")
    print(f"Signal line: {signal_func_line.tolist()}")
    print(f"Histogram: {histogram_func.tolist()}")
    
    # Compare results
    print(f"\nComparison:")
    macd_match = macd_line.equals(macd_func_line)
    signal_match = signal_line.equals(signal_func_line)
    histogram_match = histogram.equals(histogram_func)
    
    print(f"MACD line matches: {macd_match}")
    print(f"Signal line matches: {signal_match}")
    print(f"Histogram matches: {histogram_match}")
    
    if not signal_match:
        print("\nSignal line mismatch details:")
        for i in range(len(signal_line)):
            if pd.isna(signal_line.iloc[i]) != pd.isna(signal_func_line.iloc[i]):
                print(f"Index {i}: step={signal_line.iloc[i]}, func={signal_func_line.iloc[i]}")
            elif not pd.isna(signal_line.iloc[i]) and abs(signal_line.iloc[i] - signal_func_line.iloc[i]) > 0.0001:
                print(f"Index {i}: step={signal_line.iloc[i]}, func={signal_func_line.iloc[i]}")

if __name__ == "__main__":
    debug_ema()
    debug_macd()
    