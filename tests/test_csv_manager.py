import pytest
import sys
import os
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.csv_manager import CSVManager
from shared_modules.data_collection.config import DataCollectionConfig

class TestCSVManager:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config(self, temp_dir):
        config = Mock(spec=DataCollectionConfig)
        config.DATA_DIR = temp_dir
        config.LIMIT_TO_50_ENTRIES = False
        return config
    
    @pytest.fixture
    def csv_manager(self, config):
        return CSVManager(config)
    
    def test_initialization(self, csv_manager, config):
        """Test proper initialization of CSV manager"""
        assert csv_manager.config == config
        assert csv_manager.data_dir == Path(config.DATA_DIR)
    
    def test_create_csv_file(self, csv_manager):
        """Test CSV file creation"""
        test_data = {
            'timestamp': 1609459200000,
            'datetime': '2021-01-01 00:00:00',
            'open': 29000.0,
            'high': 29500.0,
            'low': 28900.0,
            'close': 29400.0,
            'volume': 1000.0
        }
        
        success = csv_manager.update_candle('BTCUSDT', '1', test_data)
        
        assert success is True
        assert os.path.exists(csv_manager.data_dir / 'BTCUSDT_1.csv')
        
        # Verify file contents
        df = pd.read_csv(csv_manager.data_dir / 'BTCUSDT_1.csv')
        assert len(df) == 1
        assert df.iloc[0]['close'] == 29400.0