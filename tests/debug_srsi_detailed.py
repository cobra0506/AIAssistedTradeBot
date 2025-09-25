# debug_srsi_detailed.py
import sys
import os
import pandas as pd
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we need to test
from simple_strategy.shared.strategy_base import (
    calculate_rsi_func,
    calculate_srsi_func,
    calculate_stochastic_func
)

def debug_srsi_calculation():
    print("\n=== Detailed SRSI Debugging ===")
    
    # Create test data
    prices = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128])
    print(f"Input prices: {prices.values}")
    
    # Step 1: Calculate RSI
    print("\n--- Step 1: Calculating RSI ---")
    rsi = calculate_rsi_func(prices, period=5)
    print(f"RSI result: {rsi.values}")
    print(f"RSI has NaN: {rsi.isna().any()}")
    print(f"RSI NaN count: {rsi.isna().sum()}")
    
    if not rsi.isna().all():
        valid_rsi = rsi.dropna()
        print(f"Valid RSI values: {valid_rsi.values}")
        print(f"RSI min: {valid_rsi.min()}, RSI max: {valid_rsi.max()}")
    
    # Step 2: Create stochastic data
    print("\n--- Step 2: Creating stochastic data ---")
    stochastic_data = pd.DataFrame({
        'high': rsi,
        'low': rsi,
        'close': rsi
    })
    print(f"Stochastic data head:\n{stochastic_data.head()}")
    
    # Step 3: Calculate stochastic
    print("\n--- Step 3: Calculating stochastic ---")
    try:
        k_percent, d_percent = calculate_stochastic_func(stochastic_data, period=5, d_period=3)
        print(f"K percent result: {k_percent.values}")
        print(f"K percent has NaN: {k_percent.isna().any()}")
        print(f"K percent NaN count: {k_percent.isna().sum()}")
        
        if not k_percent.isna().all():
            valid_k = k_percent.dropna()
            print(f"Valid K values: {valid_k.values}")
            print(f"K min: {valid_k.min()}, K max: {valid_k.max()}")
        
        print(f"D percent result: {d_percent.values}")
        print(f"D percent has NaN: {d_percent.isna().any()}")
        print(f"D percent NaN count: {d_percent.isna().sum()}")
        
    except Exception as e:
        print(f"❌ Stochastic calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Final SRSI result
    print("\n--- Step 4: Final SRSI result ---")
    srsi = calculate_srsi_func(prices, period=5)
    print(f"Final SRSI result: {srsi.values}")
    print(f"SRSI has NaN: {srsi.isna().any()}")
    print(f"SRSI NaN count: {srsi.isna().sum()}")

def test_with_more_data():
    print("\n=== Testing with more data ===")
    
    # Create more varied test data
    prices = pd.Series([
        100, 105, 95, 110, 90, 115, 85, 120, 80, 125, 75, 130, 70, 135, 65,
        140, 60, 145, 55, 150, 50, 155, 45, 160, 40, 165, 35, 170, 30, 175
    ])
    print(f"Extended prices: {prices.values}")
    
    # Calculate SRSI
    srsi = calculate_srsi_func(prices, period=5)
    print(f"Extended SRSI result: {srsi.values}")
    print(f"Extended SRSI has NaN: {srsi.isna().any()}")
    print(f"Extended SRSI NaN count: {srsi.isna().sum()}")
    
    if not srsi.isna().all():
        valid_srsi = srsi.dropna()
        print(f"Valid extended SRSI values: {valid_srsi.values}")
        print(f"Extended SRSI min: {valid_srsi.min()}, max: {valid_srsi.max()}")

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 DETAILED SRSI DEBUGGING")
    print("=" * 80)
    
    debug_srsi_calculation()
    test_with_more_data()