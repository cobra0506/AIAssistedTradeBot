import unittest
import tempfile
import shutil
import os
import json
import threading
import time
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '..')

from config import DataCollectionConfig
from csv_manager import CSVManager
from websocket_handler import WebSocketHandler

class TestWebSocketHandler(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = DataCollectionConfig()
        self.config.DATA_DIR = self.test_dir
        self.config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        self.config.TIMEFRAMES = ['1m', '5m']
        
        self.csv_manager = CSVManager(self.test_dir, 10)
        self.ws_handler = WebSocketHandler(self.config, self.csv_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.ws_handler.running:
            self.ws_handler.stop()
        shutil.rmtree(self.test_dir)
    
    def test_on_message_closed_candle(self):
        """Test handling of closed candle message"""
        # Create a mock WebSocket message for a closed candle
        message = {
            "topic": "kline.1m.BTCUSDT",
            "data": [{
                "start": "1625097600000",
                "open": "35000",
                "high": "35100",
                "low": "34900",
                "close": "35050",
                "volume": "100",
                "turnover": "3500000",
                "confirm": "1"
            }]
        }
        
        # Process the message
        self.ws_handler.on_message(None, json.dumps(message))
        
        # Check that data was written to CSV
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['open'], '35000')
    
    def test_on_message_open_candle(self):
        """Test handling of open (forming) candle message"""
        # Create a mock WebSocket message for an open candle
        message = {
            "topic": "kline.1m.BTCUSDT",
            "data": [{
                "start": "1625097600000",
                "open": "35000",
                "high": "35100",
                "low": "34900",
                "close": "35050",
                "volume": "100",
                "turnover": "3500000",
                "confirm": "0"
            }]
        }
        
        # Process the message
        self.ws_handler.on_message(None, json.dumps(message))
        
        # Check that data was NOT written to CSV (candle is still forming)
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        self.assertEqual(len(data), 0)
        
        # Check that candle is stored in current_candles
        self.assertIn('BTCUSDT_1m', self.ws_handler.current_candles)
    
    def test_on_error(self):
        """Test error handling"""
        # Mock error
        error = "Connection error"
        
        # Should not raise an exception
        self.ws_handler.on_error(None, error)
    
    @patch('websocket.WebSocketApp')
    def test_connect(self, mock_websocket):
        """Test WebSocket connection"""
        # Mock WebSocketApp
        mock_ws = MagicMock()
        mock_websocket.return_value = mock_ws
        
        # Connect
        self.ws_handler.connect()
        
        # Check that WebSocketApp was created with correct parameters
        mock_websocket.assert_called_once()
        self.assertEqual(mock_websocket.call_args[0][0], self.config.WS_URL)
    
    @patch('websocket.WebSocketApp')
    def test_start_and_stop(self, mock_websocket):
        """Test starting and stopping WebSocket handler"""
        # Mock WebSocketApp
        mock_ws = MagicMock()
        mock_websocket.return_value = mock_ws
        
        # Start
        self.ws_handler.start()
        self.assertTrue(self.ws_handler.running)
        
        # Stop
        self.ws_handler.stop()
        self.assertFalse(self.ws_handler.running)
        mock_ws.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()