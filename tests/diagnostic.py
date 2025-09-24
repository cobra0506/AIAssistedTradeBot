import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=== Diagnostic Script ===")
print(f"Python path: {sys.path[0]}")
print(f"Current directory: {os.getcwd()}")

try:
    print("\n1. Testing config import...")
    from shared_modules.data_collection.config import DataCollectionConfig
    print("   ✅ Config import successful")
except Exception as e:
    print(f"   ❌ Config import failed: {e}")

try:
    print("\n2. Testing optimized_data_fetcher import...")
    from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
    print("   ✅ OptimizedDataFetcher import successful")
except Exception as e:
    print(f"   ❌ OptimizedDataFetcher import failed: {e}")

try:
    print("\n3. Testing websocket_handler import...")
    from shared_modules.data_collection.websocket_handler import WebSocketHandler
    print("   ✅ WebSocketHandler import successful")
except Exception as e:
    print(f"   ❌ WebSocketHandler import failed: {e}")

try:
    print("\n4. Testing csv_manager import...")
    from shared_modules.data_collection.csv_manager import CSVManager
    print("   ✅ CSVManager import successful")
except Exception as e:
    print(f"   ❌ CSVManager import failed: {e}")

try:
    print("\n5. Testing hybrid_system import...")
    from shared_modules.data_collection.hybrid_system import HybridTradingSystem
    print("   ✅ HybridSystem import successful")
except Exception as e:
    print(f"   ❌ HybridSystem import failed: {e}")

print("\n=== Diagnostic Complete ===")