import pandas as pd
import os

def check_existing_data_format():
    """Check the format of existing data files"""
    data_dir = "data"  # Adjust if your data is elsewhere
    
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' not found")
        return
    
    print(f"=== Checking data in {data_dir} ===")
    
    for symbol in ["BTCUSDT", "ETHUSDT"]:
        symbol_dir = os.path.join(data_dir, symbol)
        if os.path.exists(symbol_dir):
            print(f"\n--- {symbol} ---")
            for file in os.listdir(symbol_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(symbol_dir, file)
                    print(f"\nFile: {file_path}")
                    
                    try:
                        # Read first few rows
                        df = pd.read_csv(file_path, nrows=3)
                        print("Columns:", df.columns.tolist())
                        print("Data types:")
                        print(df.dtypes)
                        print("\nFirst 2 rows:")
                        print(df.head(2))
                        
                        # Check if there's a datetime column
                        if 'datetime' in df.columns:
                            print(f"\nDatetime column format: {df['datetime'].iloc[0]}")
                        elif 'timestamp' in df.columns:
                            print(f"\nTimestamp column format: {df['timestamp'].iloc[0]}")
                        
                    except Exception as e:
                        print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_existing_data_format()