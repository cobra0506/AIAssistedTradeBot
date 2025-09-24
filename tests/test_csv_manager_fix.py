import pytest
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared_modules.data_collection.csv_manager import CSVManager
from shared_modules.data_collection.config import DataCollectionConfig

def test_csv_manager_data_dir_fix():
    """Test that CSVManager properly stores data_dir as Path object"""
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock config
        config = Mock(spec=DataCollectionConfig)
        config.DATA_DIR = temp_dir  # This is a string
        config.LIMIT_TO_50_ENTRIES = False
        
        # Create CSVManager instance
        csv_manager = CSVManager(config)
        
        # Test that data_dir is stored as Path object
        assert isinstance(csv_manager.data_dir, Path), f"data_dir should be Path object, got {type(csv_manager.data_dir)}"
        assert csv_manager.data_dir == Path(temp_dir), f"data_dir should match config path"
        
        print("✅ CSVManager data_dir fix verified!")

def test_csv_manager_functionality():
    """Test that CSVManager still works correctly after the fix"""
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a mock config
        config = Mock(spec=DataCollectionConfig)
        config.DATA_DIR = temp_dir
        config.LIMIT_TO_50_ENTRIES = False
        
        # Create CSVManager instance
        csv_manager = CSVManager(config)
        
        # Test basic functionality
        test_data = {
            'timestamp': 1609459200000,
            'datetime': '2021-01-01 00:00:00',
            'open': 29000.0,
            'high': 29500.0,
            'low': 28900.0,
            'close': 29400.0,
            'volume': 1000.0
        }
        
        # Test update_candle method
        success = csv_manager.update_candle('BTCUSDT', '1', test_data)
        assert success is True
        
        # Verify file was created
        csv_file = Path(temp_dir) / 'BTCUSDT_1.csv'
        assert csv_file.exists()
        
        # Verify file contents
        import pandas as pd
        df = pd.read_csv(csv_file)
        assert len(df) == 1
        assert df.iloc[0]['close'] == 29400.0
        
        print("✅ CSVManager functionality verified after fix!")

if __name__ == "__main__":
    print("Testing CSVManager fix...")
    test_csv_manager_data_dir_fix()
    test_csv_manager_functionality()
    print("🎉 All CSVManager fix tests passed!")