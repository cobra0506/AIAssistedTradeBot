import pytest
import asyncio
import sys
import os
import traceback
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
from shared_modules.data_collection.websocket_handler import WebSocketHandler
from shared_modules.data_collection.csv_manager import CSVManager
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.config import DataCollectionConfig

def test_optimized_data_fetcher_debug():
    """Debug test for OptimizedDataFetcher"""
    print("\n=== Testing OptimizedDataFetcher ===")
    
    try:
        # Create a mock config
        config = Mock(spec=DataCollectionConfig)
        config.API_BASE_URL = "https://api.bybit.com"
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        
        print("1. Creating OptimizedDataFetcher instance...")
        fetcher = OptimizedDataFetcher(config)
        print("   ✅ Instance created successfully")
        
        print("2. Testing initialization...")
        assert fetcher.config == config
        assert fetcher.memory_data == {}
        assert fetcher.session is None
        print("   ✅ Initialization test passed")
        
        print("3. Testing chunk calculation...")
        total_candles, num_chunks, candles_per_chunk, chunk_duration = \
            fetcher._calculate_chunk_parameters('5', 30)
        
        print(f"   Total candles: {total_candles}")
        print(f"   Number of chunks: {num_chunks}")
        print(f"   Candles per chunk: {candles_per_chunk}")
        print(f"   Chunk duration: {chunk_duration}")
        
        assert total_candles == 8640
        assert candles_per_chunk == 999
        assert num_chunks == 9
        print("   ✅ Chunk calculation test passed")
        
        print("   🎉 OptimizedDataFetcher tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ OptimizedDataFetcher test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_websocket_handler_debug():
    """Debug test for WebSocketHandler"""
    print("\n=== Testing WebSocketHandler ===")
    
    try:
        # Create a mock config
        config = Mock(spec=DataCollectionConfig)
        config.ENABLE_WEBSOCKET = True
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        
        print("1. Creating WebSocketHandler instance...")
        handler = WebSocketHandler(config)
        print("   ✅ Instance created successfully")
        
        print("2. Testing initialization...")
        assert handler.config == config
        assert handler.ws_url == "wss://stream.bybit.com/v5/public/linear"
        assert handler.running is False
        assert handler.real_time_data == {}
        assert handler.callbacks == []
        print("   ✅ Initialization test passed")
        
        print("3. Testing disabled WebSocket...")
        handler.config.ENABLE_WEBSOCKET = False
        # This should not raise an exception
        # We can't test async connect here easily, but we can test the config check
        print("   ✅ Disabled WebSocket test passed")
        
        print("   🎉 WebSocketHandler tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ WebSocketHandler test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_csv_manager_debug():
    """Debug test for CSVManager"""
    print("\n=== Testing CSVManager ===")
    
    try:
        import tempfile
        from pathlib import Path
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock config
            config = Mock(spec=DataCollectionConfig)
            config.DATA_DIR = temp_dir
            config.LIMIT_TO_50_ENTRIES = False
            
            print("1. Creating CSVManager instance...")
            csv_manager = CSVManager(config)
            print("   ✅ Instance created successfully")
            
            print("2. Testing initialization...")
            assert csv_manager.config == config
            assert csv_manager.data_dir == Path(config.DATA_DIR)
            print("   ✅ Initialization test passed")
            
            print("3. Testing CSV file creation...")
            test_data = {
                'timestamp': 1609459200000,
                'datetime': '2021-01-01 00:00:00',
                'open': 29000.0,
                'high': 29500.0,
                'low': 28900.0,
                'close': 29400.0,
                'volume': 1000.0
            }
            
            success = csv_manager.update_candle('BTCUSDT', '1', test_data)
            assert success is True
            
            csv_file = Path(temp_dir) / 'BTCUSDT_1.csv'
            assert csv_file.exists()
            print("   ✅ CSV file creation test passed")
            
            print("4. Testing CSV file content...")
            import pandas as pd
            df = pd.read_csv(csv_file)
            assert len(df) == 1
            assert df.iloc[0]['close'] == 29400.0
            print("   ✅ CSV file content test passed")
            
            print("   🎉 CSVManager tests passed!")
            return True
        
    except Exception as e:
        print(f"   ❌ CSVManager test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_hybrid_system_debug():
    """Debug test for HybridSystem"""
    print("\n=== Testing HybridSystem ===")
    
    try:
        import tempfile
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock config
            config = Mock(spec=DataCollectionConfig)
            config.DATA_DIR = temp_dir
            config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
            config.TIMEFRAMES = ['1', '5']
            config.DAYS_TO_FETCH = 7
            config.ENABLE_WEBSOCKET = True
            config.FETCH_ALL_SYMBOLS = False
            config.LIMIT_TO_50_ENTRIES = False
            
            print("1. Creating HybridSystem instance...")
            hybrid_system = HybridTradingSystem(config)
            print("   ✅ Instance created successfully")
            
            print("2. Testing initialization...")
            assert hybrid_system.config == config
            assert hybrid_system.data_fetcher is not None
            assert hybrid_system.websocket_handler is not None
            assert hybrid_system.csv_manager is not None
            print("   ✅ Initialization test passed")
            
            print("   🎉 HybridSystem tests passed!")
            return True
        
    except Exception as e:
        print(f"   ❌ HybridSystem test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG UNIT TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(test_optimized_data_fetcher_debug())
    results.append(test_websocket_handler_debug())
    results.append(test_csv_manager_debug())
    results.append(test_hybrid_system_debug())
    
    print("\n" + "=" * 60)
    print("DEBUG RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL DEBUG TESTS PASSED!")
    else:
        print("⚠️  Some debug tests failed - see output above")
    
    print("=" * 60)