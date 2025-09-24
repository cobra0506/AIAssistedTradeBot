# test_data_feeder.py - Tests for DataFeeder component
import unittest
import tempfile
import shutil
import os
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add the parent directory to the path so we can import shared module
import sys
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from shared.data_feeder import DataFeeder

class TestDataFeeder(unittest.TestCase):
    """Test cases for DataFeeder component"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.data_feeder = DataFeeder(data_dir=self.temp_dir, memory_limit_percent=90)
        
        # Create sample test data
        self.create_sample_data()
    
    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)
    
    def create_sample_data(self):
        """Create sample CSV files for testing"""
        symbols = ['BTCUSDT', 'ETHUSDT']
        timeframes = ['1m', '5m']
        
        base_time = datetime(2023, 1, 1, 0, 0, 0)
        
        for symbol in symbols:
            for timeframe in timeframes:
                data = []
                
                # Generate sample data
                if timeframe == '1m':
                    periods = 1440  # 24 hours of 1-minute data
                    delta = timedelta(minutes=1)
                else:  # 5m
                    periods = 288   # 24 hours of 5-minute data
                    delta = timedelta(minutes=5)
                
                current_time = base_time
                base_price = 50000 if symbol == 'BTCUSDT' else 3000
                
                for i in range(periods):
                    timestamp = int(current_time.timestamp() * 1000)
                    
                    # Generate realistic price movement
                    price_change = (i % 10 - 5) * 10  # Small random-like movement
                    open_price = base_price + price_change
                    close_price = open_price + (i % 3 - 1) * 5
                    high_price = max(open_price, close_price) + abs(i % 7) * 3
                    low_price = min(open_price, close_price) - abs(i % 5) * 2
                    volume = abs(i % 100) * 1000
                    
                    data.append({
                        'timestamp': timestamp,
                        'datetime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'close': close_price,
                        'volume': volume
                    })
                    
                    current_time += delta
                
                # Write to CSV file
                file_path = Path(self.temp_dir) / f"{symbol}_{timeframe}.csv"
                df = pd.DataFrame(data)
                df.to_csv(file_path, index=False)
    
    def test_init(self):
        """Test DataFeeder initialization"""
        self.assertEqual(str(self.data_feeder.data_dir), self.temp_dir)
        self.assertEqual(self.data_feeder.memory_limit_percent, 90)
        self.assertEqual(len(self.data_feeder.data_cache), 0)
    
    def test_load_single_symbol_timeframe(self):
        """Test loading single symbol and timeframe"""
        success = self.data_feeder.load_data(['BTCUSDT'], ['1m'])
        self.assertTrue(success)
        
        # Check cache
        self.assertIn('BTCUSDT', self.data_feeder.data_cache)
        self.assertIn('1m', self.data_feeder.data_cache['BTCUSDT'])
        
        # Check data
        df = self.data_feeder.data_cache['BTCUSDT']['1m']
        self.assertEqual(len(df), 1440)  # 24 hours of 1-minute data
    
    def test_load_multiple_symbols_timeframes(self):
        """Test loading multiple symbols and timeframes"""
        symbols = ['BTCUSDT', 'ETHUSDT']
        timeframes = ['1m', '5m']
        
        success = self.data_feeder.load_data(symbols, timeframes)
        self.assertTrue(success)
        
        # Check all symbols and timeframes are loaded
        for symbol in symbols:
            self.assertIn(symbol, self.data_feeder.data_cache)
            for timeframe in timeframes:
                self.assertIn(timeframe, self.data_feeder.data_cache[symbol])
    
    def test_get_data_at_timestamp(self):
        """Test getting data at specific timestamp"""
        # Load data first
        self.data_feeder.load_data(['BTCUSDT'], ['1m'])
        
        # Test with datetime
        test_time = datetime(2023, 1, 1, 12, 30, 0)
        data = self.data_feeder.get_data_at_timestamp('BTCUSDT', '1m', test_time)
        
        self.assertIsNotNone(data)
        self.assertIn('open', data)
        self.assertIn('high', data)
        self.assertIn('low', data)
        self.assertIn('close', data)
        self.assertIn('volume', data)
        self.assertIn('timestamp_ms', data)
    
    def test_get_latest_data(self):
        """Test getting latest data"""
        # Load data first
        self.data_feeder.load_data(['BTCUSDT'], ['1m'])
        
        # Test getting latest data
        latest_data = self.data_feeder.get_latest_data('BTCUSDT', '1m', lookback_periods=5)
        
        self.assertIsNotNone(latest_data)
        self.assertEqual(len(latest_data), 5)
        
        # Check that data is in chronological order
        for i in range(1, len(latest_data)):
            self.assertGreater(latest_data[i]['timestamp_ms'], latest_data[i-1]['timestamp_ms'])
    
    def test_get_multi_timeframe_data(self):
        """Test getting multi-timeframe data"""
        # Load data first
        self.data_feeder.load_data(['BTCUSDT'], ['1m', '5m'])
        
        # Test multi-timeframe retrieval
        test_time = datetime(2023, 1, 1, 12, 30, 0)
        multi_tf_data = self.data_feeder.get_multi_timeframe_data('BTCUSDT', ['1m', '5m'], test_time)
        
        self.assertIsNotNone(multi_tf_data)
        self.assertIn('1m', multi_tf_data)
        self.assertIn('5m', multi_tf_data)
    
    def test_memory_usage(self):
        """Test memory usage tracking"""
        # Load some data
        self.data_feeder.load_data(['BTCUSDT'], ['1m', '5m'])
        
        # Get memory usage
        memory_info = self.data_feeder.get_memory_usage()
        
        self.assertIn('system_memory_percent', memory_info)
        self.assertIn('cache_size_mb', memory_info)
        self.assertIn('loaded_symbols', memory_info)
        self.assertIn('total_files_loaded', memory_info)
        
        # Check that our data is reflected in memory info
        self.assertIn('BTCUSDT', memory_info['loaded_symbols'])
        self.assertEqual(memory_info['total_files_loaded'], 2)
    
    def test_clear_cache(self):
        """Test cache clearing functionality"""
        # Load data first
        self.data_feeder.load_data(['BTCUSDT', 'ETHUSDT'], ['1m', '5m'])
        
        # Verify data is loaded
        self.assertEqual(len(self.data_feeder.data_cache), 2)
        
        # Clear specific symbol
        self.data_feeder.clear_cache('BTCUSDT')
        
        # Verify only BTCUSDT is cleared
        self.assertEqual(len(self.data_feeder.data_cache), 1)
        self.assertNotIn('BTCUSDT', self.data_feeder.data_cache)
        self.assertIn('ETHUSDT', self.data_feeder.data_cache)
        
        # Clear all remaining cache
        self.data_feeder.clear_cache()
        
        # Verify all cache is cleared
        self.assertEqual(len(self.data_feeder.data_cache), 0)
    
    def test_date_filtering(self):
        """Test date range filtering"""
        # Load data with date range
        start_date = datetime(2023, 1, 1, 6, 0, 0)  # 6:00 AM
        end_date = datetime(2023, 1, 1, 18, 0, 0)    # 6:00 PM
        
        success = self.data_feeder.load_data(['BTCUSDT'], ['1m'], start_date, end_date)
        self.assertTrue(success)
        
        # Check that data is filtered correctly
        df = self.data_feeder.data_cache['BTCUSDT']['1m']
        self.assertGreaterEqual(df.index.min(), start_date)
        self.assertLessEqual(df.index.max(), end_date)

if __name__ == '__main__':
    unittest.main()