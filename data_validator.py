import re
from datetime import datetime
from typing import List, Dict, Any

class DataValidator:
    @staticmethod
    def validate_timestamp(timestamp_str: str) -> bool:
        """Validate timestamp format and value"""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt <= datetime.now()
        except ValueError:
            return False
    
    @staticmethod
    def validate_price(value: str) -> bool:
        """Validate price/volume values"""
        try:
            num = float(value)
            return num > 0
        except ValueError:
            return False
    
    @staticmethod
    def validate_candle(candle: Dict[str, Any]) -> bool:
        """Validate a single candle record"""
        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        
        # Check all required fields exist
        if not all(field in candle for field in required_fields):
            return False
        
        # Validate timestamp
        if not DataValidator.validate_timestamp(candle['timestamp']):
            return False
        
        # Validate price fields
        price_fields = ['open', 'high', 'low', 'close', 'volume', 'turnover']
        if not all(DataValidator.validate_price(candle[field]) for field in price_fields):
            return False
        
        # Validate price relationships
        try:
            open_price = float(candle['open'])
            high_price = float(candle['high'])
            low_price = float(candle['low'])
            close_price = float(candle['close'])
            
            if not (low_price <= high_price and 
                    low_price <= open_price <= high_price and 
                    low_price <= close_price <= high_price):
                return False
        except ValueError:
            return False
        
        return True
    
    @staticmethod
    def validate_data_consistency(data: List[Dict[str, Any]]) -> bool:
        """Validate consistency of a list of candles"""
        if not data:
            return True
        
        # Sort by timestamp
        sorted_data = sorted(data, key=lambda x: x['timestamp'])
        
        # Check for gaps and validate each candle
        prev_timestamp = None
        for candle in sorted_data:
            if not DataValidator.validate_candle(candle):
                return False
            
            current_timestamp = datetime.fromisoformat(candle['timestamp'])
            if prev_timestamp and (current_timestamp - prev_timestamp).total_seconds() > 300:
                print(f"Warning: Large gap detected between {prev_timestamp} and {current_timestamp}")
            
            prev_timestamp = current_timestamp
        
        return True
    
    @staticmethod
    def clean_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean data by removing invalid records"""
        cleaned_data = []
        for candle in data:
            if DataValidator.validate_candle(candle):
                cleaned_data.append(candle)
            else:
                print(f"Removed invalid candle: {candle}")
        
        return cleaned_data