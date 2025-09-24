# test_end_to_end.py
import pytest
import asyncio
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.config import DataCollectionConfig
from tests.test_mock_strategy import MockStrategyBase

class TestEndToEnd:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config(self, temp_dir):
        config = Mock(spec=DataCollectionConfig)
        config.DATA_DIR = temp_dir
        config.SYMBOLS = ['BTCUSDT']
        config.TIMEFRAMES = ['1']
        config.DAYS_TO_FETCH = 1
        config.ENABLE_WEBSOCKET = True
        config.FETCH_ALL_SYMBOLS = False
        config.LIMIT_TO_50_ENTRIES = False
        return config
    
    @pytest.mark.asyncio
    async def test_complete_data_flow(self, config):
        """Test complete data flow from API to strategy consumption"""
        # Initialize system
        hybrid_system = HybridTradingSystem(config)
        strategy = MockStrategyBase(config.DATA_DIR)
        
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
        
        # Mock WebSocket data
        mock_websocket_data = {
            'timestamp': 1609459320000,
            'datetime': '2021-01-01 00:02:00',
            'open': 29500.0,
            'high': 29700.0,
            'low': 29400.0,
            'close': 29600.0,
            'volume': 1500.0
        }
        
        # Test historical data collection
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch:
            mock_fetch.return_value = mock_historical_data
            
            await hybrid_system.collect_historical_data()
            
            # Verify data was stored
            assert (config.DATA_DIR / 'BTCUSDT_1.csv').exists()
            
            # Verify strategy can load data
            df = strategy.load_historical_data('BTCUSDT', '1')
            assert len(df) == 2
            assert df.iloc[-1]['close'] == 29500.0
        
        # Test WebSocket data integration
        with patch.object(hybrid_system.websocket_handler, 'connect') as mock_connect:
            mock_connect.return_value = AsyncMock()
            
            # Start WebSocket
            task = asyncio.create_task(hybrid_system.start_websocket())
            
            # Simulate WebSocket data
            await hybrid_system.websocket_handler._process_candle_data(
                'BTCUSDT', '1', mock_websocket_data
            )
            
            # Stop WebSocket
            hybrid_system.websocket_handler.running = False
            await task
            
            # Verify data was updated
            df = strategy.load_historical_data('BTCUSDT', '1')
            assert len(df) == 3
            assert df.iloc[-1]['close'] == 29600.0
        
        # Test strategy calculations
        latest = strategy.get_latest_candle('BTCUSDT', '1')
        assert latest['close'] == 29600.0
        
        sma = strategy.calculate_sma('BTCUSDT', '1', 2)
        assert not sma.empty
        assert sma.iloc[-1] == 29550.0  # (29500 + 29600) / 2
        
        rsi = strategy.calculate_rsi('BTCUSDT', '1', 2)
        assert not rsi.empty
    
    @pytest.mark.asyncio
    async def test_error_recovery(self, config):
        """Test system recovery from errors"""
        hybrid_system = HybridTradingSystem(config)
        
        # Test API failure recovery
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")
            
            # Should not crash
            await hybrid_system.collect_historical_data()
            
            # System should still be functional
            assert hybrid_system.data_fetcher is not None
        
        # Test WebSocket failure recovery
        with patch.object(hybrid_system.websocket_handler, 'connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection Error")
            
            # Should not crash
            await hybrid_system.start_websocket()
            
            # System should still be functional
            assert hybrid_system.websocket_handler is not None
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, config):
        """Test system performance under load"""
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT', 'DOTUSDT']
        config.TIMEFRAMES = ['1', '5', '15']
        
        hybrid_system = HybridTradingSystem(config)
        
        # Mock large dataset
        mock_data = []
        for i in range(1000):  # 1000 candles per symbol/timeframe
            mock_data.append({
                'timestamp': 1609459200000 + i * 60000,
                'open': 29000.0 + i,
                'high': 29500.0 + i,
                'low': 28900.0 + i,
                'close': 29400.0 + i,
                'volume': 1000.0 + i
            })
        
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch:
            mock_fetch.return_value = mock_data
            
            # Time the operation
            import time
            start_time = time.time()
            
            await hybrid_system.collect_historical_data()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Should complete within reasonable time (adjust as needed)
            assert duration < 30.0  # 30 seconds
            
            # Verify all files were created
            for symbol in config.SYMBOLS:
                for timeframe in config.TIMEFRAMES:
                    assert (config.DATA_DIR / f'{symbol}_{timeframe}.csv').exists()