import pytest
import asyncio
import sys
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.config import DataCollectionConfig

class TestHybridSystem:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config(self, temp_dir):
        config = Mock(spec=DataCollectionConfig)
        config.DATA_DIR = temp_dir
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        config.DAYS_TO_FETCH = 7
        config.ENABLE_WEBSOCKET = True
        config.FETCH_ALL_SYMBOLS = False
        config.LIMIT_TO_50_ENTRIES = False
        return config
    
    @pytest.fixture
    def hybrid_system(self, config):
        return HybridTradingSystem(config)
    
    @pytest.mark.asyncio
    async def test_initialization(self, hybrid_system, config):
        """Test proper initialization of hybrid system"""
        assert hybrid_system.config == config
        assert hybrid_system.data_fetcher is not None
        assert hybrid_system.websocket_handler is not None
        assert hybrid_system.csv_manager is not None
    
    @pytest.mark.asyncio
    async def test_historical_data_collection_workflow(self, hybrid_system):
        """Test complete historical data collection workflow"""
        # Mock the data fetcher
        mock_historical_data = [
            {
                'timestamp': 1609459200000,
                'open': 29000.0,
                'high': 29500.0,
                'low': 28900.0,
                'close': 29400.0,
                'volume': 1000.0
            }
        ]
        
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch:
            mock_fetch.return_value = mock_historical_data
            
            # Run historical data collection
            await hybrid_system.collect_historical_data()
            
            # Verify data was fetched and stored
            mock_fetch.assert_called_once()
            
            # Verify CSV files were created
            assert (hybrid_system.config.DATA_DIR / 'BTCUSDT_1.csv').exists()
            assert (hybrid_system.config.DATA_DIR / 'BTCUSDT_5.csv').exists()