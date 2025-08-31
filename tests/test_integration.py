import unittest
import tempfile
import shutil
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '..')

from config import DataCollectionConfig
from csv_manager import CSVManager
from historical_fetcher import HistoricalDataFetcher
from websocket_handler import WebSocketHandler
from data_validator import DataValidator

class TestDataCollection(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = DataCollectionConfig()
        self.config.DATA_DIR = self.test_dir
        self.config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        self.config.TIMEFRAMES = ['1m', '5m']
        
        self.csv_manager = CSVManager(self.test_dir, 10)
        self.validator = DataValidator()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_csv_operations(self):
        """Test CSV read/write operations"""
        # Test data
        test_data = [
            {
                'timestamp': datetime.now().isoformat(),
                'open': '50000',
                'high': '50100',
                'low': '49900',
                'close': '50050',
                'volume': '100',
                'turnover': '5000000'
            }
        ]
        
        # Write data
        self.csv_manager.write_data('BTCUSDT', '1m', test_data)
        
        # Read data
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['open'], '50000')
        
        # Test max entries limit
        for i in range(15):
            test_data[0]['timestamp'] = (datetime.now() + timedelta(minutes=i)).isoformat()
            self.csv_manager.write_data('BTCUSDT', '1m', test_data)
        
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        self.assertEqual(len(data), 10)  # Should be limited to max_entries
    
    def test_data_validation(self):
        """Test data validation functionality"""
        # Valid candle
        valid_candle = {
            'timestamp': datetime.now().isoformat(),
            'open': '50000',
            'high': '50100',
            'low': '49900',
            'close': '50050',
            'volume': '100',
            'turnover': '5000000'
        }
        
        self.assertTrue(self.validator.validate_candle(valid_candle))
        
        # Invalid candle (missing field)
        invalid_candle = valid_candle.copy()
        del invalid_candle['volume']
        self.assertFalse(self.validator.validate_candle(invalid_candle))
        
        # Invalid candle (bad price relationship)
        invalid_candle = valid_candle.copy()
        invalid_candle['high'] = '49800'  # Lower than low
        self.assertFalse(self.validator.validate_candle(invalid_candle))
    
    @patch('requests.Session.get')
    def test_historical_fetcher(self, mock_get):
        """Test historical data fetching"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'retCode': 0,
            'result': {
                'list': [
                    ['1625097600000', '35000', '35100', '34900', '35050', '100', '3500000']
                ]
            }
        }
        mock_get.return_value = mock_response
        
        fetcher = HistoricalDataFetcher(self.config, self.csv_manager)
        
        # Test single fetch
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        data = fetcher.fetch_historical_klines('BTCUSDT', '1m', start_time, end_time)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['open'], '35000')
        
        # Test CSV write after fetch
        fetcher.fetch_all_historical_data(1)
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        self.assertGreater(len(data), 0)
    
    def test_data_consistency(self):
        """Test data consistency validation"""
        # Create test data with gaps
        base_time = datetime.now()
        data = []
        
        for i in range(5):
            candle = {
                'timestamp': (base_time + timedelta(minutes=i*2)).isoformat(),  # 2-minute gaps
                'open': '50000',
                'high': '50100',
                'low': '49900',
                'close': '50050',
                'volume': '100',
                'turnover': '5000000'
            }
            data.append(candle)
        
        # Should detect gaps but still return True
        self.assertTrue(self.validator.validate_data_consistency(data))
        
        # Add invalid candle
        data.append({
            'timestamp': 'invalid-timestamp',
            'open': '50000',
            'high': '50100',
            'low': '49900',
            'close': '50050',
            'volume': '100',
            'turnover': '5000000'
        })
        
        self.assertFalse(self.validator.validate_data_consistency(data))

if __name__ == '__main__':
    unittest.main()