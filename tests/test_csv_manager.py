import unittest
import tempfile
import shutil
import os
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from csv_manager import CSVManager

class TestCSVManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.csv_manager = CSVManager(self.test_dir, 10)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_write_and_read_data(self):
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
    
    def test_max_entries_limit(self):
        """Test max entries limit functionality"""
        # Add more entries than the limit
        for i in range(15):
            test_data = [{
                'timestamp': (datetime.now() + timedelta(minutes=i)).isoformat(),
                'open': '50000',
                'high': '50100',
                'low': '49900',
                'close': '50050',
                'volume': '100',
                'turnover': '5000000'
            }]
            self.csv_manager.write_data('BTCUSDT', '1m', test_data)
        
        # Should be limited to max_entries
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        self.assertEqual(len(data), 10)
    
    def test_data_sorting(self):
        """Test that data is properly sorted by timestamp"""
        # Add data in reverse order
        for i in range(5, 0, -1):
            test_data = [{
                'timestamp': (datetime.now() + timedelta(minutes=i)).isoformat(),
                'open': '50000',
                'high': '50100',
                'low': '49900',
                'close': '50050',
                'volume': '100',
                'turnover': '5000000'
            }]
            self.csv_manager.write_data('BTCUSDT', '1m', test_data)
        
        # Data should be sorted in ascending order
        data = self.csv_manager.read_data('BTCUSDT', '1m')
        for i in range(1, len(data)):
            self.assertGreaterEqual(data[i]['timestamp'], data[i-1]['timestamp'])

if __name__ == '__main__':
    unittest.main()