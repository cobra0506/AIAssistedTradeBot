import pandas as pd
import os

def check_csv_files():
    data_dir = 'data'
    for timeframe in ['1', '5', '15']:
        filename = os.path.join(data_dir, f'BTCUSDT_{timeframe}.csv')
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            print(f"\n{filename}:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Newest timestamp: {df['timestamp'].iloc[0]}")
            print(f"  Oldest timestamp: {df['timestamp'].iloc[-1]}")
            print(f"  Sample data:")
            print(df.head(3))

check_csv_files()