"""
Verify Data Collection Status
============================

This script checks what data has been collected and provides a summary.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from shared_modules.data_collection.config import DataCollectionConfig
from shared_modules.data_collection.csv_manager import CSVManager

def main():
    print("🔍 Data Collection Verification")
    print("=" * 50)
    
    # Get config
    config = DataCollectionConfig()
    csv_manager = CSVManager(config)
    
    # Check data directory
    data_dir = Path(config.DATA_DIR)
    print(f"Data directory: {data_dir.absolute()}")
    print(f"Directory exists: {data_dir.exists()}")
    
    if not data_dir.exists():
        print("❌ Data directory does not exist!")
        return
    
    # List all CSV files
    csv_files = list(data_dir.glob("*.csv"))
    print(f"Total CSV files: {len(csv_files)}")
    
    if not csv_files:
        print("❌ No CSV files found!")
        return
    
    # Group by symbol
    symbols = {}
    for file in csv_files:
        # Extract symbol from filename (format: SYMBOL_TIMEFRAME.csv)
        parts = file.stem.split('_')
        if len(parts) >= 2:
            symbol = parts[0]
            timeframe = parts[1]
            
            if symbol not in symbols:
                symbols[symbol] = []
            symbols[symbol].append(timeframe)
    
    print(f"\n📊 Symbols collected: {len(symbols)}")
    for symbol, timeframes in sorted(symbols.items()):
        print(f"  {symbol}: {len(timeframes)} timeframes ({', '.join(sorted(timeframes))})")
    
    # Check data for a specific symbol
    if symbols:
        first_symbol = list(symbols.keys())[0]
        first_timeframe = symbols[first_symbol][0]
        
        print(f"\n📋 Sample data for {first_symbol} ({first_timeframe}):")
        data = csv_manager.read_csv_data(first_symbol, first_timeframe)
        
        if data:
            print(f"  Records: {len(data)}")
            print(f"  Date range: {data[0]['datetime']} to {data[-1]['datetime']}")
            print("  Latest record:")
            latest = data[-1]
            print(f"    Timestamp: {latest['timestamp']}")
            print(f"    DateTime: {latest['datetime']}")
            print(f"    Open: {latest['open']}")
            print(f"    High: {latest['high']}")
            print(f"    Low: {latest['low']}")
            print(f"    Close: {latest['close']}")
            print(f"    Volume: {latest['volume']}")
        else:
            print("  No data found")
    
    # Check for your configured symbols
    print(f"\n🔍 Checking for configured symbols:")
    configured_symbols = config.SYMBOLS
    print(f"Configured symbols: {configured_symbols}")
    
    missing_symbols = [s for s in configured_symbols if s not in symbols]
    if missing_symbols:
        print(f"❌ Missing symbols: {missing_symbols}")
    else:
        print("✅ All configured symbols found!")
    
    # Check for recent data (last 24 hours)
    import time
    current_time = int(time.time() * 1000)
    day_ago = current_time - (24 * 60 * 60 * 1000)
    
    recent_data = False
    for symbol, timeframes in symbols.items():
        for timeframe in timeframes:
            data = csv_manager.read_csv_data(symbol, timeframe)
            if data and data[-1]['timestamp'] > day_ago:
                recent_data = True
                break
        if recent_data:
            break
    
    if recent_data:
        print("✅ Recent data collected (within last 24 hours)")
    else:
        print("⚠️  No recent data found (older than 24 hours)")
    
    print("\n✅ Data collection verification complete!")

if __name__ == "__main__":
    main()