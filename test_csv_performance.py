import os
import time
import pandas as pd
import numpy as np

# --- A simple RSI calculation to simulate strategy work ---
def calculate_rsi(prices, period=14):
    """Calculate RSI properly"""
    if len(prices) < period + 1:
        return np.array([50.0] * len(prices))  # Default to neutral
    
    # Calculate price changes
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum()/period
    down = -seed[seed < 0].sum()/period
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - (100./(1.+rs))
    
    # Calculate the rest of RSI values
    for i in range(period, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        
        up = (up*(period-1) + upval)/period
        down = (down*(period-1) + downval)/period
        rs = up/down
        rsi[i] = 100. - (100./(1.+rs))
    
    return rsi

# --- The main performance test ---
def run_performance_test():
    """Scans the data dir and simulates running a strategy on all files."""
    start_time = time.time()
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print(f"❌ Error: Data directory '{data_dir}' not found.")
        return

    symbols = set()
    intervals = set()
    files_processed = 0
    
    print("🚀 Starting performance test...")
    print("   (Reading CSV and calculating RSI for each file)\n")

    try:
        for filename in os.listdir(data_dir):
            if filename.endswith('.csv'):
                # Expected format: SYMBOL_INTERVAL.csv (e.g., BTCUSDT_1.csv)
                parts = filename[:-4].split('_')
                if len(parts) == 2:
                    symbol = parts[0]
                    interval = parts[1]
                    symbols.add(symbol)
                    intervals.add(interval)
                    
                    file_path = os.path.join(data_dir, filename)
                    
                    # --- The Core Task: Read and Process ---
                    file_start_time = time.time()
                    df = pd.read_csv(file_path)
                    
                    # Simulate a strategy calculation
                    closes = df['close'].values
                    _ = calculate_rsi(closes, period=14)
                    # --- End of Core Task ---
                    
                    files_processed += 1
                    file_end_time = time.time()
                    print(f"   Processed {filename} in {(file_end_time - file_start_time)*1000:.2f} ms")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        return

    end_time = time.time()
    total_duration = end_time - start_time

    # --- Print Summary Statistics ---
    print("\n--- Test Complete ---")
    print(f"✅ Processed {files_processed} files in {total_duration:.2f} seconds.")
    print(f"📊 Found {len(symbols)} unique symbols and {len(intervals)} unique intervals.")
    
    if files_processed > 0:
        avg_time_per_file = (total_duration / files_processed) * 1000
        print(f"⏱️ Average time per file: {avg_time_per_file:.2f} ms")
        
        # Estimate total time for all 2725 files
        estimated_total_files = 545 * 5 # 545 symbols * 5 intervals
        estimated_total_time = (total_duration / files_processed) * estimated_total_files
        print(f"🔮 Estimated time for all {estimated_total_files} files: {estimated_total_time:.2f} seconds.")
        
        if estimated_total_time < 60:
            print("✅ Result: The CSV-based approach should be fast enough for a 1-minute loop.")
        else:
            print("⚠️ Result: The CSV-based approach might be too slow. Consider Redis optimization.")

if __name__ == "__main__":
    run_performance_test()