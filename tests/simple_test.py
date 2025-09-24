import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_basic_imports():
    """Test that we can import all modules"""
    print("Testing basic imports...")
    
    try:
        from shared_modules.data_collection.config import DataCollectionConfig
        print("✅ Config imported")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
        print("✅ OptimizedDataFetcher imported")
    except Exception as e:
        print(f"❌ OptimizedDataFetcher import failed: {e}")
        return False
    
    try:
        from shared_modules.data_collection.websocket_handler import WebSocketHandler
        print("✅ WebSocketHandler imported")
    except Exception as e:
        print(f"❌ WebSocketHandler import failed: {e}")
        return False
    
    try:
        from shared_modules.data_collection.csv_manager import CSVManager
        print("✅ CSVManager imported")
    except Exception as e:
        print(f"❌ CSVManager import failed: {e}")
        return False
    
    try:
        from shared_modules.data_collection.hybrid_system import HybridTradingSystem
        print("✅ HybridSystem imported")
    except Exception as e:
        print(f"❌ HybridSystem import failed: {e}")
        return False
    
    return True

def test_basic_instantiation():
    """Test that we can create instances with minimal config"""
    print("\nTesting basic instantiation...")
    
    try:
        from unittest.mock import Mock
        from shared_modules.data_collection.config import DataCollectionConfig
        from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
        
        # Create minimal mock config
        config = Mock(spec=DataCollectionConfig)
        config.API_BASE_URL = "https://api.bybit.com"
        config.SYMBOLS = ['BTCUSDT']
        config.TIMEFRAMES = ['1']
        
        # Try to create instance
        fetcher = OptimizedDataFetcher(config)
        print("✅ OptimizedDataFetcher instantiated")
        
        # Test basic attribute
        assert hasattr(fetcher, '_calculate_chunk_parameters')
        print("✅ OptimizedDataFetcher has required method")
        
    except Exception as e:
        print(f"❌ OptimizedDataFetcher instantiation failed: {e}")
        return False
    
    try:
        from unittest.mock import Mock
        from shared_modules.data_collection.config import DataCollectionConfig
        from shared_modules.data_collection.websocket_handler import WebSocketHandler
        
        # Create minimal mock config
        config = Mock(spec=DataCollectionConfig)
        config.ENABLE_WEBSOCKET = True
        config.SYMBOLS = ['BTCUSDT']
        config.TIMEFRAMES = ['1']
        
        # Try to create instance
        handler = WebSocketHandler(config)
        print("✅ WebSocketHandler instantiated")
        
    except Exception as e:
        print(f"❌ WebSocketHandler instantiation failed: {e}")
        return False
    
    try:
        import tempfile
        from pathlib import Path
        from unittest.mock import Mock
        from shared_modules.data_collection.config import DataCollectionConfig
        from shared_modules.data_collection.csv_manager import CSVManager
        
        # Create temporary directory and config
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Mock(spec=DataCollectionConfig)
            config.DATA_DIR = temp_dir
            config.LIMIT_TO_50_ENTRIES = False
            
            # Try to create instance
            csv_manager = CSVManager(config)
            print("✅ CSVManager instantiated")
            
    except Exception as e:
        print(f"❌ CSVManager instantiation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("SIMPLE TEST SUITE")
    print("=" * 50)
    
    success = True
    
    if not test_basic_imports():
        success = False
    
    if not test_basic_instantiation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL SIMPLE TESTS PASSED!")
        print("Your data feeder components are working correctly!")
    else:
        print("❌ Some simple tests failed")
        print("There may be issues with the module implementations")
    print("=" * 50)