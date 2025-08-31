import pandas as pd
import os
from datetime import datetime, timedelta

def check_data_continuity():
    data_dir = 'data'
    
    for timeframe in ['1', '5', '15']:
        filename = os.path.join(data_dir, f'BTCUSDT_{timeframe}.csv')
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            
            # Convert timestamps to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Sort by timestamp (oldest first)
            df = df.sort_values('timestamp')
            
            # Check for gaps
            timeframe_minutes = int(timeframe)
            expected_interval = timedelta(minutes=timeframe_minutes)
            
            gaps = []
            for i in range(1, len(df)):
                actual_interval = df.iloc[i]['timestamp'] - df.iloc[i-1]['timestamp']
                if actual_interval > expected_interval:
                    gaps.append((df.iloc[i-1]['timestamp'], df.iloc[i]['timestamp'], actual_interval))
            
            print(f"\n{timeframe}m data:")
            print(f"  Total records: {len(df)}")
            print(f"  Time range: {df.iloc[0]['timestamp']} to {df.iloc[-1]['timestamp']}")
            
            if gaps:
                print(f"  ❌ Found {len(gaps)} gaps:")
                for start, end, interval in gaps:
                    print(f"    Gap from {start} to {end} ({interval})")
            else:
                print("  ✅ No gaps found")

check_data_continuity()