# Test data loading
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

# Now import from the correct path
from simple_strategy.shared.data_feeder import DataFeeder

print("=== Testing Data Loading ===")

# Create data feeder
feeder = DataFeeder(data_dir='data')

# Try to load BTCUSDT 1-minute data
df = feeder._load_csv_file('BTCUSDT', '1m')

if df is not None:
    print(f"✅ Successfully loaded {len(df)} rows")
    print(f"Date range: {df.index.min()} to {df.index.max()}")
    print(f"Columns: {list(df.columns)}")
else:
    print("❌ Failed to load data")

print("=== Test Complete ===")