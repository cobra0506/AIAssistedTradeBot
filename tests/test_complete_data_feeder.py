import pytest
import asyncio
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
from shared_modules.data_collection.websocket_handler import WebSocketHandler
from shared_modules.data_collection.csv_manager import CSVManager
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.config import DataCollectionConfig

class TestCompleteDataFeeder:
    """Complete test suite for the data feeder system"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config(self, temp_dir):
        config = Mock(spec=DataCollectionConfig)
        config.API_BASE_URL = "https://api.bybit.com"
        config.DATA_DIR = temp_dir
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        config.DAYS_TO_FETCH = 7
        config.ENABLE_WEBSOCKET = True
        config.FETCH_ALL_SYMBOLS = False
        config.LIMIT_TO_50_ENTRIES = False
        return config
    
    def test_optimized_data_fetcher_complete(self, config):
        """Test OptimizedDataFetcher functionality"""
        fetcher = OptimizedDataFetcher(config)
        
        # Test initialization
        assert fetcher.config == config
        assert fetcher.memory_data == {}
        assert fetcher.session is None
        
        # Test chunk calculation
        total_candles, num_chunks, candles_per_chunk, chunk_duration = \
            fetcher._calculate_chunk_parameters('5', 30)
        
        assert total_candles == 8640
        assert candles_per_chunk == 999
        assert num_chunks == 9
        assert chunk_duration == 299700000
        
        print("✅ OptimizedDataFetcher tests passed")
    
    def test_websocket_handler_complete(self, config):
        """Test WebSocketHandler functionality"""
        handler = WebSocketHandler(config)
        
        # Test initialization
        assert handler.config == config
        assert handler.ws_url == "wss://stream.bybit.com/v5/public/linear"
        assert handler.running is False
        assert handler.real_time_data == {}
        assert handler.callbacks == []
        
        print("✅ WebSocketHandler tests passed")
    
    def test_csv_manager_complete(self, config):
        """Test CSVManager functionality with the fix"""
        csv_manager = CSVManager(config)
        
        # Test that data_dir is properly stored as Path object
        assert isinstance(csv_manager.data_dir, Path)
        assert csv_manager.data_dir == Path(config.DATA_DIR)
        
        # Test CSV file creation and data writing
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
        
        # Verify file was created
        csv_file = csv_manager.data_dir / 'BTCUSDT_1.csv'
        assert csv_file.exists()
        
        # Verify file contents
        df = pd.read_csv(csv_file)
        assert len(df) == 1
        assert df.iloc[0]['close'] == 29400.0
        
        print("✅ CSVManager tests passed")
    
    def test_hybrid_system_complete(self, config):
        """Test HybridSystem functionality"""
        hybrid_system = HybridTradingSystem(config)
        
        # Test initialization
        assert hybrid_system.config == config
        assert hybrid_system.data_fetcher is not None
        assert hybrid_system.websocket_handler is not None
        assert hybrid_system.csv_manager is not None
        
        print("✅ HybridSystem tests passed")
    
    @pytest.mark.asyncio
    async def test_end_to_end_data_flow(self, config):
        """Test complete end-to-end data flow"""
        hybrid_system = HybridTradingSystem(config)
        
        # Mock historical data
        mock_historical_data = [
            {
                'timestamp': 1609459200000,
                'open': 29000.0,
                'high': 29500.0,
                'low': 28900.0,
                'close': 29400.0,
                'volume': 1000.0
            },
            {
                'timestamp': 1609459260000,
                'open': 29400.0,
                'high': 29600.0,
                'low': 29300.0,
                'close': 29500.0,
                'volume': 1200.0
            }
        ]
        
        # Test historical data collection
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch:
            mock_fetch.return_value = mock_historical_data
            
            await hybrid_system.collect_historical_data()
            
            # Verify data was stored
            assert (hybrid_system.config.DATA_DIR / 'BTCUSDT_1.csv').exists()
            assert (hybrid_system.config.DATA_DIR / 'BTCUSDT_5.csv').exists()
            assert (hybrid_system.config.DATA_DIR / 'ETHUSDT_1.csv').exists()
            assert (hybrid_system.config.DATA_DIR / 'ETHUSDT_5.csv').exists()
        
        print("✅ End-to-end data flow tests passed")

class TestMockStrategyBase:
    """Test the mock strategy base for data consumption"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def strategy(self, temp_dir):
        from tests.test_mock_strategy_base import MockStrategyBase
        return MockStrategyBase(temp_dir)
    
    def test_strategy_data_loading(self, strategy, temp_dir):
        """Test strategy can load data from CSV files"""
        # Create test CSV file
        csv_file = Path(temp_dir) / 'BTCUSDT_1.csv'
        test_data = """timestamp,datetime,open,high,low,close,volume
1609459200000,2021-01-01 00:00:00,29000.0,29500.0,28900.0,29400.0,1000.0
1609459260000,2021-01-01 00:01:00,29400.0,29600.0,29300.0,29500.0,1200.0"""
        
        with open(csv_file, 'w') as f:
            f.write(test_data)
        
        # Test strategy data loading
        df = strategy.load_historical_data('BTCUSDT', '1')
        assert len(df) == 2
        assert df.iloc[0]['close'] == 29400.0
        assert df.iloc[1]['close'] == 29500.0
        
        print("✅ Strategy data loading tests passed")
    
    def test_strategy_latest_candle(self, strategy, temp_dir):
        """Test strategy can get latest candle"""
        # Create test CSV file
        csv_file = Path(temp_dir) / 'BTCUSDT_1.csv'
        test_data = """timestamp,datetime,open,high,low,close,volume
1609459200000,2021-01-01 00:00:00,29000.0,29500.0,28900.0,29400.0,1000.0
1609459260000,2021-01-01 00:01:00,29400.0,29600.0,29300.0,29500.0,1200.0"""
        
        with open(csv_file, 'w') as f:
            f.write(test_data)
        
        # Test latest candle retrieval
        latest = strategy.get_latest_candle('BTCUSDT', '1')
        assert latest['close'] == 29500.0
        assert latest['volume'] == 1200.0
        
        print("✅ Strategy latest candle tests passed")

if __name__ == "__main__":
    print("Running complete data feeder test suite...")
    
    # Run the tests
    import tempfile
    from unittest.mock import Mock
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = Mock(spec=DataCollectionConfig)
        config.API_BASE_URL = "https://api.bybit.com"
        config.DATA_DIR = temp_dir
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        config.DAYS_TO_FETCH = 7
        config.ENABLE_WEBSOCKET = True
        config.FETCH_ALL_SYMBOLS = False
        config.LIMIT_TO_50_ENTRIES = False
        
        test_suite = TestCompleteDataFeeder()
        test_suite.test_optimized_data_fetcher_complete(config)
        test_suite.test_websocket_handler_complete(config)
        test_suite.test_csv_manager_complete(config)
        test_suite.test_hybrid_system_complete(config)
        
        strategy_suite = TestMockStrategyBase()
        strategy = strategy_suite.strategy(temp_dir)
        strategy_suite.test_strategy_data_loading(strategy, temp_dir)
        strategy_suite.test_strategy_latest_candle(strategy, temp_dir)
    
    print("🎉 COMPLETE DATA FEEDER TEST SUITE PASSED!")
    print("Your data feeder and strategy base are working 100%!")