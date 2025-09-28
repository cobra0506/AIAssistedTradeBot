"""
Debug test for data access in backtest engine
This test focuses specifically on checking if data is accessed correctly
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.shared.data_feeder import DataFeeder
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover
from simple_strategy.backtester.risk_manager import RiskManager

class TestDataAccess(unittest.TestCase):
    """Test class specifically for debugging data access"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data
        self._create_test_data()
        
        # Initialize components
        self.data_feeder = DataFeeder(data_dir=self.temp_dir)
        self.risk_manager = RiskManager()
        
        print(f"🔧 Test data created in: {self.temp_dir}")
    
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_data(self):
        """Create test data"""
        np.random.seed(42)
        
        # Create 3 days of 1-minute data
        start_time = datetime(2023, 1, 1, 0, 0)
        timestamps = []
        unix_timestamps = []
        
        for day in range(3):
            for minute in range(1440):  # 1440 minutes per day
                dt = start_time + timedelta(days=day, minutes=minute)
                timestamps.append(dt)
                unix_timestamps.append(int(dt.timestamp() * 1000))
        
        # Create price data
        base_price = 20000.0
        prices = []
        
        for i, timestamp in enumerate(timestamps):
            # Generate realistic price movement
            daily_volatility = 0.015 / np.sqrt(1440)
            trend_factor = 0.0008 * i / 1440
            cycle_factor = 0.3 * np.sin(2 * np.pi * i / 1440)
            random_factor = np.random.normal(0, daily_volatility)
            
            price = base_price * (1 + trend_factor + cycle_factor + random_factor)
            prices.append(price)
        
        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': unix_timestamps,
            'datetime': timestamps,
            'open': prices,
            'high': [p * 1.001 for p in prices],
            'low': [p * 0.999 for p in prices],
            'close': prices,
            'volume': [np.random.randint(100, 1000) for _ in range(len(prices))]
        })
        
        # Format datetime as string
        data['datetime'] = data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to CSV
        csv_filename = f"BTCUSDT_1m.csv"
        csv_path = os.path.join(self.temp_dir, csv_filename)
        data.to_csv(csv_path, index=False)
        
        print(f"🔧 Created {len(data)} rows of test data")
    
    def test_data_access(self):
        """Test if data is accessed correctly"""
        print("\n🧪 Testing data access...")
        
        try:
            # Load data
            success = self.data_feeder.load_data(['BTCUSDT'], ['1m'], 
                                                datetime(2023, 1, 1), datetime(2023, 1, 2))
            self.assertTrue(success, "Data should load successfully")
            
            # Get data for a specific timestamp
            target_timestamp = datetime(2023, 1, 1, 12, 0)  # Noon on first day
            
            all_data = self.data_feeder.get_data_for_symbols(['BTCUSDT'], ['1m'], 
                                                          datetime(2023, 1, 1), datetime(2023, 1, 2))
            
            # Create backtester engine to test _get_data_for_timestamp
            strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy_builder.add_indicator('rsi', rsi, period=14)
            strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                          indicator='rsi', overbought=70, oversold=30)
            strategy = strategy_builder.build()
            
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager
            )
            
            # Test the data access method
            timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], target_timestamp)
            
            print(f"🔧 Timestamp data keys: {list(timestamp_data.keys())}")
            print(f"🔧 BTCUSDT data keys: {list(timestamp_data['BTCUSDT'].keys())}")
            
            btc_data = timestamp_data['BTCUSDT']['1m']
            print(f"🔧 BTCUSDT 1m data shape: {btc_data.shape}")
            print(f"🔧 BTCUSDT 1m data date range: {btc_data.index.min()} to {btc_data.index.max()}")
            
            # Check if we have enough data for indicator calculation
            self.assertGreater(len(btc_data), 14, "Should have more than 14 rows for RSI calculation")
            
            # Test if indicators can be calculated with this data
            rsi_result = rsi(btc_data['close'], period=14)
            print(f"🔧 RSI result length: {len(rsi_result)}")
            print(f"🔧 RSI NaN count: {rsi_result.isna().sum()}")
            print(f"🔧 RSI valid count: {rsi_result.notna().sum()}")
            
            # Should have some valid RSI values
            self.assertGreater(rsi_result.notna().sum(), 0, "Should have some valid RSI values")
            
            print("✅ Data access test PASSED")
            
        except Exception as e:
            print(f"❌ Data access test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_strategy_signals_with_correct_data(self):
        """Test if strategy generates signals correctly with proper data"""
        print("\n🧪 Testing strategy signals with correct data...")
        
        try:
            # Load data
            success = self.data_feeder.load_data(['BTCUSDT'], ['1m'], 
                                                datetime(2023, 1, 1), datetime(2023, 1, 2))
            self.assertTrue(success, "Data should load successfully")
            
            # Create strategy
            strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy_builder.add_indicator('rsi', rsi, period=14)
            strategy_builder.add_indicator('sma_short', sma, period=20)
            strategy_builder.add_indicator('sma_long', sma, period=50)
            strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                          indicator='rsi', overbought=70, oversold=30)
            strategy_builder.add_signal_rule('ma_cross', ma_crossover, 
                                          fast_ma='sma_short', slow_ma='sma_long')
            strategy = strategy_builder.build()
            
            # Get data for a specific timestamp
            target_timestamp = datetime(2023, 1, 1, 12, 0)  # Noon on first day
            
            all_data = self.data_feeder.get_data_for_symbols(['BTCUSDT'], ['1m'], 
                                                          datetime(2023, 1, 1), datetime(2023, 1, 2))
            
            # Create backtester engine
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager
            )
            
            # Get data for timestamp
            timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], target_timestamp)
            
            # Generate signals
            signals = strategy.generate_signals(timestamp_data)
            
            print(f"🔧 Generated signals: {signals}")
            
            # Check if we got valid signals
            self.assertIn('BTCUSDT', signals, "Should have signals for BTCUSDT")
            self.assertIn('1m', signals['BTCUSDT'], "Should have signals for 1m timeframe")
            
            signal_value = signals['BTCUSDT']['1m']
            self.assertIn(signal_value, ['BUY', 'SELL', 'HOLD'], f"Signal should be BUY, SELL, or HOLD, got {signal_value}")
            
            print(f"🔧 Signal for BTCUSDT 1m: {signal_value}")
            
            print("✅ Strategy signals test PASSED")
            
        except Exception as e:
            print(f"❌ Strategy signals test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    print("🚀 Starting Data Access Debug Test")
    print("=" * 50)
    
    unittest.main(verbosity=2)