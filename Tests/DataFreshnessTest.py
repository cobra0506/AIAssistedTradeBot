import pandas as pd
import os
from datetime import datetime, timedelta

def check_data_freshness():
    data_dir = 'data'
    current_time = datetime.now()
    
    for timeframe in ['1', '5', '15']:
        filename = os.path.join(data_dir, f'BTCUSDT_{timeframe}.csv')
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            newest_time = datetime.fromisoformat(df['timestamp'].iloc[0])
            time_diff = current_time - newest_time
            
            print(f"\n{timeframe}m data:")
            print(f"  Newest timestamp: {newest_time}")
            print(f"  Current time: {current_time}")
            print(f"  Time difference: {time_diff}")
            
            # Check if data is fresh (within expected timeframe)
            if timeframe == '1' and time_diff < timedelta(minutes=2):
                print("  ✅ Data is fresh")
            elif timeframe == '5' and time_diff < timedelta(minutes=6):
                print("  ✅ Data is fresh")
            elif timeframe == '15' and time_diff < timedelta(minutes=16):
                print("  ✅ Data is fresh")
            else:
                print("  ❌ Data is not fresh enough")

check_data_freshness()