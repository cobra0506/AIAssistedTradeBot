import pytest
import asyncio
import sys
import os
import json
from unittest.mock import Mock, patch, AsyncMock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.websocket_handler import WebSocketHandler
from shared_modules.data_collection.config import DataCollectionConfig

class TestWebSocketHandler:
    @pytest.fixture
    def config(self):
        config = Mock(spec=DataCollectionConfig)
        config.ENABLE_WEBSOCKET = True
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        config.TIMEFRAMES = ['1', '5']
        return config
    
    @pytest.fixture
    def handler(self, config):
        return WebSocketHandler(config)
    
    def test_initialization(self, handler, config):
        """Test proper initialization of WebSocket handler"""
        assert handler.config == config
        assert handler.ws_url == "wss://stream.bybit.com/v5/public/linear"
        assert handler.running is False
        assert handler.real_time_data == {}
        assert handler.callbacks == []
    
    @pytest.mark.asyncio
    async def test_connect_disabled(self, handler):
        """Test connection when WebSocket is disabled"""
        handler.config.ENABLE_WEBSOCKET = False
        await handler.connect()
        assert handler.running is False
    
    @pytest.mark.asyncio
    async def test_process_candle_message(self, handler):
        """Test processing of candle messages"""
        message = {
            "topic": "candle.1.BTCUSDT",
            "data": {
                "start": 1609459200000,
                "open": "29000.0",
                "high": "29500.0",
                "low": "28900.0",
                "close": "29400.0",
                "volume": "1000.0",
                "confirm": True
            }
        }
        
        # Mock CSV manager
        handler.csv_manager = Mock()
        handler.csv_manager.update_candle = Mock(return_value=True)
        
        await handler._process_message(json.dumps(message))
        
        # Verify CSV manager was called with correct data
        handler.csv_manager.update_candle.assert_called_once()
        call_args = handler.csv_manager.update_candle.call_args
        assert call_args[0][0] == 'BTCUSDT'  # symbol
        assert call_args[0][1] == '1'  # timeframe
        assert call_args[0][2]['open'] == 29000.0
        assert call_args[0][2]['close'] == 29400.0