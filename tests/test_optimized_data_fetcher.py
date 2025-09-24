import pytest
import asyncio
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.optimized_data_fetcher import OptimizedDataFetcher
from shared_modules.data_collection.config import DataCollectionConfig

class TestOptimizedDataFetcher:
    @pytest.fixture
    def config(self):
        config = Mock(spec=DataCollectionConfig)
        config.API_BASE_URL = "https://api.bybit.com"
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        return config
    
    @pytest.fixture
    def fetcher(self, config):
        return OptimizedDataFetcher(config)
    
    @pytest.mark.asyncio
    async def test_initialization(self, fetcher, config):
        """Test proper initialization of data fetcher"""
        assert fetcher.config == config
        assert fetcher.memory_data == {}
        assert fetcher.session is None
        assert fetcher.fetch_stats['total_requests'] == 0
    
    @pytest.mark.asyncio
    async def test_calculate_chunk_parameters(self, fetcher):
        """Test chunk calculation logic"""
        total_candles, num_chunks, candles_per_chunk, chunk_duration = \
            fetcher._calculate_chunk_parameters('5', 30)
        
        assert total_candles == 8640  # 30 days * 24 hours * 12 candles per hour (5min)
        assert candles_per_chunk == 999  # Max allowed by Bybit
        assert num_chunks == 9  # ceil(8640 / 999)
        assert chunk_duration == 999 * 5 * 60 * 1000  # milliseconds

    @pytest.mark.asyncio
    async def test_fetch_historical_data_success(self, fetcher):
        """Test successful historical data fetching"""
        # Mock the session
        fetcher.session = Mock()
        
        mock_response_data = {
            'retCode': 0,
            'result': {
                'list': [
                    [1609459200000, '29000.0', '29500.0', '28900.0', '29400.0', '1000.0']
                ]
            }
        }
        
        # Mock the response object
        mock_response = Mock()
        mock_response.status = 200
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        with patch.object(fetcher.session, 'get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await fetcher.fetch_historical_data_fast(['BTCUSDT'], ['1'], 1)
            
            assert len(result) == 1
            assert result[0]['timestamp'] == 1609459200000
            assert result[0]['open'] == 29000.0
            assert result[0]['close'] == 29400.0