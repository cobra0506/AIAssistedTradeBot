# test_data_files.py - Test script to check data files
import os
import pandas as pd
from pathlib import Path

def test_data_files():
    data_dir = Path("data")
    
    print(f"Checking data directory: {data_dir}")
    print(f"Directory exists: {data_dir.exists()}")
    
    if data_dir.exists():
        files = list(data_dir.glob("*.csv"))
        print(f"Found {len(files)} CSV files:")
        
        for file in files:
            print(f"\n--- File: {file.name} ---")
            try:
                # Read first few rows to check format
                df = pd.read_csv(file, nrows=5)
                print(f"Columns: {list(df.columns)}")
                print(f"Shape: {df.shape}")
                print(f"First row:\n{df.iloc[0]}")
                
                # Check if required columns exist
                required_columns = ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    print(f"ERROR: Missing required columns: {missing_columns}")
                else:
                    print("All required columns present")
                
            except Exception as e:
                print(f"ERROR reading file: {str(e)}")
    else:
        print("Data directory does not exist!")

if __name__ == "__main__":
    test_data_files()