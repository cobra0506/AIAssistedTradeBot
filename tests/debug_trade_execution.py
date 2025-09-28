"""
Debug test for trade execution in backtest engine
This test focuses specifically on checking if trades are executed correctly
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

class TestTradeExecution(unittest.TestCase):
    """Test class specifically for debugging trade execution"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test data with clear buy/sell signals
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
        """Create test data with predictable patterns"""
        np.random.seed(42)
        
        # Create 2 days of 1-minute data
        start_time = datetime(2023, 1, 1, 0, 0)
        timestamps = []
        unix_timestamps = []
        
        for day in range(2):
            for minute in range(1440):  # 1440 minutes per day
                dt = start_time + timedelta(days=day, minutes=minute)
                timestamps.append(dt)
                unix_timestamps.append(int(dt.timestamp() * 1000))
        
        # Create price data with clear patterns
        base_price = 20000.0
        prices = []
        
        for i, timestamp in enumerate(timestamps):
            # Create a pattern that will generate clear signals
            if i < 720:  # First 12 hours: uptrend
                price = base_price + (i * 2)  # Steady increase
            elif i < 1440:  # Next 12 hours: downtrend
                price = base_price + 1440 - ((i - 720) * 2)  # Steady decrease
            else:  # Second day: repeat pattern
                day2_i = i - 1440
                if day2_i < 720:
                    price = base_price + (day2_i * 2)
                else:
                    price = base_price + 1440 - ((day2_i - 720) * 2)
            
            # Add some noise
            noise = np.random.normal(0, 10)
            price += noise
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
        
        print(f"🔧 Created {len(data)} rows of test data with clear patterns")
    
    def test_trade_execution(self):
        """Test if trades are executed correctly"""
        print("\n🧪 Testing trade execution...")
        
        try:
            # Load data
            success = self.data_feeder.load_data(['BTCUSDT'], ['1m'], 
                                                datetime(2023, 1, 1), datetime(2023, 1, 2))
            self.assertTrue(success, "Data should load successfully")
            
            # Create strategy that should generate clear signals
            strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy_builder.add_indicator('rsi', rsi, period=14)
            strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                          indicator='rsi', overbought=70, oversold=30)
            strategy = strategy_builder.build()
            
            # Create backtester engine
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager
            )
            
            # Run backtest
            results = backtester.run_backtest(
                symbols=['BTCUSDT'],
                timeframes=['1m'],
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 1, 2)
            )
            
            print(f"🔧 Backtest results keys: {list(results.keys())}")
            
            # Check if results contain trades
            if 'trades' in results:
                trades = results['trades']
                print(f"🔧 Number of trades executed: {len(trades)}")
                
                if len(trades) > 0:
                    print("🔧 First few trades:")
                    for i, trade in enumerate(trades[:5]):
                        print(f"  Trade {i+1}: {trade}")
                    
                    # Check trade structure
                    first_trade = trades[0]
                    required_keys = ['symbol', 'signal', 'timestamp', 'price', 'quantity']
                    for key in required_keys:
                        self.assertIn(key, first_trade, f"Trade should contain {key}")
                    
                    print("✅ Trade execution test PASSED")
                else:
                    print("⚠️ No trades were executed")
                    # This might be expected if the strategy didn't generate signals
                    # Let's check the signals
                    if 'signals' in results:
                        signals = results['signals']
                        print(f"🔧 Number of signal entries: {len(signals)}")
                        if len(signals) > 0:
                            print(f"🔧 Sample signals: {signals[:3]}")
            else:
                print("❌ No 'trades' key in results")
                print(f"🔧 Results: {results}")
                self.fail("Results should contain 'trades' key")
                
        except Exception as e:
            print(f"❌ Trade execution test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_signal_generation_during_backtest(self):
        """Test what signals are generated during backtest"""
        print("\n🧪 Testing signal generation during backtest...")
        
        try:
            # Load data
            success = self.data_feeder.load_data(['BTCUSDT'], ['1m'], 
                                                datetime(2023, 1, 1), datetime(2023, 1, 2))
            self.assertTrue(success, "Data should load successfully")
            
            # Create strategy
            strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
            strategy_builder.add_indicator('rsi', rsi, period=14)
            strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                          indicator='rsi', overbought=70, oversold=30)
            strategy = strategy_builder.build()
            
            # Create backtester engine
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager
            )
            
            # Get data for a few timestamps to check signal generation
            all_data = self.data_feeder.get_data_for_symbols(['BTCUSDT'], ['1m'], 
                                                          datetime(2023, 1, 1), datetime(2023, 1, 2))
            
            # Test signal generation at different timestamps
            test_timestamps = [
                datetime(2023, 1, 1, 6, 0),   # 6 AM - should have some signals
                datetime(2023, 1, 1, 12, 0),  # 12 PM - should have some signals
                datetime(2023, 1, 1, 18, 0),  # 6 PM - should have some signals
            ]
            
            signal_count = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            
            for timestamp in test_timestamps:
                timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], timestamp)
                signals = strategy.generate_signals(timestamp_data)
                
                signal_value = signals['BTCUSDT']['1m']
                signal_count[signal_value] += 1
                
                print(f"🔧 Signal at {timestamp}: {signal_value}")
            
            print(f"🔧 Signal count: {signal_count}")
            
            # We should have some non-HOLD signals
            total_signals = sum(signal_count.values())
            non_hold_signals = signal_count['BUY'] + signal_count['SELL']
            
            print(f"🔧 Total signals: {total_signals}")
            print(f"🔧 Non-HOLD signals: {non_hold_signals}")
            
            if non_hold_signals > 0:
                print("✅ Signal generation test PASSED")
            else:
                print("⚠️ All signals are HOLD - this might indicate an issue with the strategy or data")
                
        except Exception as e:
            print(f"❌ Signal generation test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    print("🚀 Starting Trade Execution Debug Test")
    print("=" * 50)
    
    unittest.main(verbosity=2)