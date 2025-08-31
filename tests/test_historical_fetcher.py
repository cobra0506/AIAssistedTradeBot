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

class TestHistoricalFetcher(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.config = DataCollectionConfig()
        self.config.DATA_DIR = self.test_dir
        self.config.SYMBOLS = ['BTCUSDT', 'ETHUSDT']
        self.config.TIMEFRAMES = ['1m', '5m']
        
        self.csv_manager = CSVManager(self.test_dir, 10)
        self.fetcher = HistoricalDataFetcher(self.config, self.csv_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    @patch('requests.Session.get')
    def test_fetch_historical_klines(self, mock_get):
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
        
        # Test single fetch
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        data = self.fetcher.fetch_historical_klines('BTCUSDT', '1m', start_time, end_time)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['open'], '35000')
        self.assertEqual(data[0]['close'], '35050')
    
    @patch('requests.Session.get')
    def test_fetch_all_historical_data(self, mock_get):
        """Test fetching all historical data"""
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
        
        # Test fetching for all symbols and timeframes
        self.fetcher.fetch_all_historical_data(1)
        
        # Check that data was written to CSV files
        for symbol in self.config.SYMBOLS:
            for timeframe in self.config.TIMEFRAMES:
                data = self.csv_manager.read_data(symbol, timeframe)
                self.assertGreater(len(data), 0)
    
    @patch('requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'retCode': 10001,
            'retMsg': 'Invalid API key'
        }
        mock_get.return_value = mock_response
        
        # Test that empty list is returned on error
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        data = self.fetcher.fetch_historical_klines('BTCUSDT', '1m', start_time, end_time)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()