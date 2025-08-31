import unittest
from datetime import datetime
import sys
sys.path.insert(0, '..')

from data_validator import DataValidator

class TestDataValidator(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.validator = DataValidator()
    
    def test_validate_timestamp(self):
        """Test timestamp validation"""
        # Valid timestamp
        valid_timestamp = datetime.now().isoformat()
        self.assertTrue(self.validator.validate_timestamp(valid_timestamp))
        
        # Invalid timestamp format
        invalid_timestamp = "2023-13-01T12:00:00"  # Invalid month
        self.assertFalse(self.validator.validate_timestamp(invalid_timestamp))
        
        # Future timestamp
        future_timestamp = (datetime.now() + timedelta(days=1)).isoformat()
        self.assertFalse(self.validator.validate_timestamp(future_timestamp))
    
    def test_validate_price(self):
        """Test price validation"""
        # Valid price
        self.assertTrue(self.validator.validate_price("50000.5"))
        
        # Invalid price (zero)
        self.assertFalse(self.validator.validate_price("0"))
        
        # Invalid price (negative)
        self.assertFalse(self.validator.validate_price("-100"))
        
        # Invalid price (non-numeric)
        self.assertFalse(self.validator.validate_price("price"))
    
    def test_validate_candle(self):
        """Test candle validation"""
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
    
    def test_validate_data_consistency(self):
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
    
    def test_clean_data(self):
        """Test data cleaning functionality"""
        # Create test data with some invalid records
        valid_candle = {
            'timestamp': datetime.now().isoformat(),
            'open': '50000',
            'high': '50100',
            'low': '49900',
            'close': '50050',
            'volume': '100',
            'turnover': '5000000'
        }
        
        invalid_candle = valid_candle.copy()
        invalid_candle['timestamp'] = 'invalid-timestamp'
        
        data = [valid_candle, invalid_candle, valid_candle]
        
        # Clean data should remove invalid records
        cleaned_data = self.validator.clean_data(data)
        self.assertEqual(len(cleaned_data), 2)
        self.assertTrue(all(self.validator.validate_candle(candle) for candle in cleaned_data))

if __name__ == '__main__':
    unittest.main()