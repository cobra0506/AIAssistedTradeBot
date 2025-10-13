# Test strategy creation
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

# Now import from the correct path
from simple_strategy.strategies.Strategy_Simple_Test import create_strategy

print("=== Testing Strategy Creation ===")

try:
    # Create strategy
    strategy = create_strategy(['BTCUSDT'], ['1m'])
    
    # Get strategy info
    info = strategy.get_strategy_info()
    print(f"✅ Strategy created successfully")
    print(f"Name: {info.get('strategy_name', 'Unknown')}")
    print(f"Version: {info.get('version', 'Unknown')}")
    
except Exception as e:
    print(f"❌ Failed to create strategy: {e}")

print("=== Test Complete ===")