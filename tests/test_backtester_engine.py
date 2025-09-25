"""
Unit tests for Backtester Engine
Tests functionality rather than just ensuring tests pass
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the components to test
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.shared.data_feeder import DataFeeder
from simple_strategy.shared.strategy_base import StrategyBase

class TestBacktesterEngine(unittest.TestCase):
    """Test suite for BacktesterEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock data feeder
        self.mock_data_feeder = Mock(spec=DataFeeder)
        
        # Create mock strategy
        self.mock_strategy = Mock(spec=StrategyBase)
        self.mock_strategy.name = "TestStrategy"
        self.mock_strategy.symbols = ["BTCUSDT"]
        self.mock_strategy.timeframes = ["1m"]
        self.mock_strategy.balance = 10000.0
        self.mock_strategy.initial_balance = 10000.0
        self.mock_strategy.positions = {}
        self.mock_strategy.trades = []
        self.mock_strategy.max_risk_per_trade = 0.01
        self.mock_strategy.max_positions = 3
        self.mock_strategy.max_portfolio_risk = 0.10
        
        # Create backtester engine
        self.backtester = BacktesterEngine(
            data_feeder=self.mock_data_feeder,
            strategy=self.mock_strategy,
            config={'processing_mode': 'sequential', 'batch_size': 100}
        )
        
        # Create sample data
        self.sample_data = self._create_sample_data()
        
    def tearDown(self):
        """Clean up after each test method"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
        
    def _create_sample_data(self):
        """Create sample market data for testing"""
        # Create timestamps
        start_time = datetime(2023, 1, 1, 0, 0)
        timestamps = [start_time + timedelta(minutes=i) for i in range(100)]
        
        # Create price data with some trend and volatility
        base_price = 20000.0
        prices = []
        
        for i, timestamp in enumerate(timestamps):
            # Add some trend and randomness
            trend = i * 10  # Upward trend
            noise = np.random.normal(0, 100)  # Random noise
            price = base_price + trend + noise
            prices.append(price)
        
        # Create DataFrame
        data = pd.DataFrame({
            'open': prices,
            'high': [p + abs(np.random.normal(0, 50)) for p in prices],
            'low': [p - abs(np.random.normal(0, 50)) for p in prices],
            'close': prices,
            'volume': [np.random.randint(100, 1000) for _ in prices]
        }, index=timestamps)
        
        return {"BTCUSDT": {"1m": data}}
    
    def test_initialization(self):
        """Test that BacktesterEngine initializes correctly"""
        # Verify components are set
        self.assertEqual(self.backtester.data_feeder, self.mock_data_feeder)
        self.assertEqual(self.backtester.strategy, self.mock_strategy)
        
        # Verify default configuration
        self.assertEqual(self.backtester.processing_mode, 'sequential')
        self.assertEqual(self.backtester.batch_size, 100)
        self.assertFalse(self.backtester.is_running)
        
        # Verify processing stats are initialized
        self.assertEqual(self.backtester.processing_stats['total_rows_processed'], 0)
        self.assertEqual(self.backtester.processing_stats['total_signals_generated'], 0)
        self.assertEqual(self.backtester.processing_stats['total_trades_executed'], 0)
    
    def test_data_validation_valid_data(self):
        """Test data validation with valid data"""
        # Test validation
        result = self.backtester._validate_data(
            self.sample_data, 
            ["BTCUSDT"], 
            ["1m"]
        )
        
        # Should return True for valid data
        self.assertTrue(result)
    
    def test_data_validation_missing_symbol(self):
        """Test data validation with missing symbol"""
        # Create data with missing symbol
        incomplete_data = {"ETHUSDT": {"1m": self.sample_data["BTCUSDT"]["1m"]}}
        
        # Test validation
        result = self.backtester._validate_data(
            incomplete_data, 
            ["BTCUSDT"],  # Requesting BTCUSDT but it's not in data
            ["1m"]
        )
        
        # Should return False for missing symbol
        self.assertFalse(result)
    
    def test_process_signals_buy_signal(self):
        """Test processing BUY signals"""
        # Set up strategy mock
        self.mock_strategy.validate_signal.return_value = True
        self.mock_strategy.calculate_position_size.return_value = 0.1
        
        # Create signals
        signals = {"BTCUSDT": {"1m": "BUY"}}
        
        # Create current data
        current_data = self.sample_data
        
        # Get timestamp
        timestamp = list(self.sample_data["BTCUSDT"]["1m"].index)[50]
        
        # Process signals
        trades = self.backtester._process_signals(signals, current_data, timestamp)
        
        # Verify trade was created
        self.assertEqual(len(trades), 1)
        
        # Verify trade details
        trade = trades[0]
        self.assertEqual(trade['symbol'], "BTCUSDT")
        self.assertEqual(trade['signal'], "BUY")
        self.assertEqual(trade['position_size'], 0.1)
        
        # Verify strategy methods were called
        self.mock_strategy.validate_signal.assert_called_once()
        self.mock_strategy.calculate_position_size.assert_called_once()
        
        # Verify position was added to strategy
        self.assertIn("BTCUSDT", self.mock_strategy.positions)
    
    def test_execute_trade_buy_insufficient_balance(self):
        """Test executing BUY trade with insufficient balance"""
        # Set up strategy with low balance
        self.mock_strategy.balance = 100.0  # Very low balance
        
        # Get timestamp
        timestamp = datetime(2023, 1, 1, 0, 0)
        
        # Execute trade
        trade = self.backtester._execute_trade(
            "BTCUSDT", 
            "BUY", 
            1.0,  # Large position size
            20000.0,  # High price
            timestamp
        )
        
        # Verify trade was not executed (returned None)
        self.assertIsNone(trade)
        
        # Verify strategy balance was not changed
        self.assertEqual(self.mock_strategy.balance, 100.0)
        
        # Verify position was not added
        self.assertNotIn("BTCUSDT", self.mock_strategy.positions)
    
    def test_get_current_price(self):
        """Test getting current price from DataFrame"""
        # Get DataFrame
        df = self.sample_data["BTCUSDT"]["1m"]
        
        # Get current price
        price = self.backtester._get_current_price(df)
        
        # Verify price is correct
        self.assertEqual(price, df['close'].iloc[-1])
    
    def test_stop_backtest(self):
        """Test stopping a running backtest"""
        # Start backtest
        self.backtester.is_running = True
        
        # Stop backtest
        self.backtester.stop_backtest()
        
        # Verify backtest is stopped
        self.assertFalse(self.backtester.is_running)
    
    def test_get_status(self):
        """Test getting backtester status"""
        # Set up backtester state
        self.backtester.is_running = True
        self.backtester.current_timestamp = datetime(2023, 1, 1, 0, 0)
        self.backtester.processing_stats['total_rows_processed'] = 100
        
        # Get status
        status = self.backtester.get_status()
        
        # Verify status
        self.assertTrue(status['is_running'])
        self.assertEqual(status['current_timestamp'], datetime(2023, 1, 1, 0, 0))
        self.assertEqual(status['processing_stats']['total_rows_processed'], 100)

if __name__ == '__main__':
    # This allows running the test file directly with Ctrl+F5
    unittest.main(verbosity=2)