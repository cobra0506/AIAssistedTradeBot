import pytest
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockStrategyBase:
    """
    Mock strategy base for testing data feeder functionality
    """
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_cache = {}
    
    def load_historical_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Load historical data from CSV files"""
        file_path = self.data_dir / f"{symbol}_{timeframe}.csv"
        
        if not file_path.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        df['timestamp'] = pd.to_datetime(df['datetime'])
        df.set_index('timestamp', inplace=True)
        
        return df
    
    def get_latest_candle(self, symbol: str, timeframe: str) -> dict:
        """Get the latest candle for a symbol and timeframe"""
        df = self.load_historical_data(symbol, timeframe)
        
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        return {
            'timestamp': int(latest.name.timestamp() * 1000),
            'datetime': latest.name.strftime('%Y-%m-%d %H:%M:%S'),
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'close': float(latest['close']),
            'volume': float(latest['volume'])
        }

class TestMockStrategyBase:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def strategy(self, temp_dir):
        return MockStrategyBase(temp_dir)
    
    def test_load_historical_data_empty(self, strategy):
        """Test loading data when no files exist"""
        df = strategy.load_historical_data('BTCUSDT', '1')
        assert df.empty
    
    def test_load_historical_data_with_files(self, strategy, temp_dir):
        """Test loading data when CSV files exist"""
        # Create test CSV file
        csv_file = Path(temp_dir) / 'BTCUSDT_1.csv'
        test_data = """timestamp,datetime,open,high,low,close,volume
1609459200000,2021-01-01 00:00:00,29000.0,29500.0,28900.0,29400.0,1000.0
1609459260000,2021-01-01 00:01:00,29400.0,29600.0,29300.0,29500.0,1200.0"""
        
        with open(csv_file, 'w') as f:
            f.write(test_data)
        
        df = strategy.load_historical_data('BTCUSDT', '1')
        
        assert len(df) == 2
        assert df.iloc[0]['close'] == 29400.0
        assert df.iloc[1]['close'] == 29500.0