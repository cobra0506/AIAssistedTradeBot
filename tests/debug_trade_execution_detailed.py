"""
Detailed debug test for trade execution
This test focuses specifically on why trades are not being executed despite signals being generated
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

class TestTradeExecutionDetailed(unittest.TestCase):
    """Test class specifically for debugging why trades aren't executed"""
    
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
        """Create test data with extreme RSI values to force signals"""
        np.random.seed(42)
        
        # Create 1 day of 1-minute data
        start_time = datetime(2023, 1, 1, 0, 0)
        timestamps = []
        unix_timestamps = []
        
        for minute in range(1440):  # 1440 minutes per day
            dt = start_time + timedelta(minutes=minute)
            timestamps.append(dt)
            unix_timestamps.append(int(dt.timestamp() * 1000))
        
        # Create price data with extreme RSI values
        base_price = 20000.0
        prices = []
        
        for i in range(len(timestamps)):
            # First half: create strong uptrend (RSI will go high)
            if i < 720:
                price = base_price + (i * 10)  # Strong uptrend
            # Second half: create strong downtrend (RSI will go low)
            else:
                price = base_price + 7200 - ((i - 720) * 10)  # Strong downtrend
            
            # Add small noise
            noise = np.random.normal(0, 5)
            price += noise
            prices.append(price)
        
        # Create DataFrame
        data = pd.DataFrame({
            'timestamp': unix_timestamps,
            'datetime': timestamps,
            'open': prices,
            'high': [p * 1.002 for p in prices],
            'low': [p * 0.998 for p in prices],
            'close': prices,
            'volume': [np.random.randint(100, 1000) for _ in range(len(prices))]
        })
        
        # Format datetime as string
        data['datetime'] = data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Save to CSV
        csv_filename = f"BTCUSDT_1m.csv"
        csv_path = os.path.join(self.temp_dir, csv_filename)
        data.to_csv(csv_path, index=False)
        
        print(f"🔧 Created {len(data)} rows of test data with extreme trends")
    
    def test_can_execute_trade_logic(self):
        """Test the _can_execute_trade logic specifically"""
        print("\n🧪 Testing _can_execute_trade logic...")
        
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
            
            # Get data for a timestamp where we expect a signal
            all_data = self.data_feeder.get_data_for_symbols(['BTCUSDT'], ['1m'], 
                                                          datetime(2023, 1, 1), datetime(2023, 1, 2))
            
            # Test at a timestamp during the uptrend (should get BUY signal)
            test_timestamp = datetime(2023, 1, 1, 10, 0)  # 10 AM
            
            timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], test_timestamp)
            signals = strategy.generate_signals(timestamp_data)
            
            print(f"🔧 Signal at {test_timestamp}: {signals}")
            
            # Test _can_execute_trade for BUY signal
            can_execute = backtester._can_execute_trade('BTCUSDT', 'BUY', test_timestamp)
            print(f"🔧 Can execute BUY trade: {can_execute}")
            
            # Test at a timestamp during the downtrend (should get SELL signal)
            test_timestamp = datetime(2023, 1, 1, 14, 0)  # 2 PM
            
            timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], test_timestamp)
            signals = strategy.generate_signals(timestamp_data)
            
            print(f"🔧 Signal at {test_timestamp}: {signals}")
            
            # Test _can_execute_trade for SELL signal
            can_execute = backtester._can_execute_trade('BTCUSDT', 'SELL', test_timestamp)
            print(f"🔧 Can execute SELL trade: {can_execute}")
            
            print("✅ _can_execute_trade logic test completed")
            
        except Exception as e:
            print(f"❌ _can_execute_trade logic test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_execute_trade_logic(self):
        """Test the _execute_trade logic specifically"""
        print("\n🧪 Testing _execute_trade logic...")
        
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
            
            # Get data for a timestamp
            all_data = self.data_feeder.get_data_for_symbols(['BTCUSDT'], ['1m'], 
                                                          datetime(2023, 1, 1), datetime(2023, 1, 2))
            
            # Test at a timestamp during the uptrend
            test_timestamp = datetime(2023, 1, 1, 10, 0)  # 10 AM
            
            timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], test_timestamp)
            
            # Execute a BUY trade
            print(f"🔧 Executing BUY trade at {test_timestamp}...")
            trade_result = backtester._execute_trade('BTCUSDT', 'BUY', test_timestamp, timestamp_data)
            
            print(f"🔧 Trade result: {trade_result}")
            
            # Check if trade was executed
            if trade_result.get('executed', False):
                print("✅ BUY trade executed successfully")
                
                # Now try to execute a SELL trade
                test_timestamp = datetime(2023, 1, 1, 14, 0)  # 2 PM
                
                timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], test_timestamp)
                
                print(f"🔧 Executing SELL trade at {test_timestamp}...")
                trade_result = backtester._execute_trade('BTCUSDT', 'SELL', test_timestamp, timestamp_data)
                
                print(f"🔧 Trade result: {trade_result}")
                
                if trade_result.get('executed', False):
                    print("✅ SELL trade executed successfully")
                else:
                    print("⚠️ SELL trade was not executed")
                    print(f"🔧 Reason: {trade_result.get('reason', 'Unknown')}")
            else:
                print("⚠️ BUY trade was not executed")
                print(f"🔧 Reason: {trade_result.get('reason', 'Unknown')}")
            
            print("✅ _execute_trade logic test completed")
            
        except Exception as e:
            print(f"❌ _execute_trade logic test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_manual_trade_execution(self):
        """Test manual trade execution step by step"""
        print("\n🧪 Testing manual trade execution...")
        
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
            
            # Get data for a timestamp
            all_data = self.data_feeder.get_data_for_symbols(['BTCUSDT'], ['1m'], 
                                                          datetime(2023, 1, 1), datetime(2023, 1, 2))
            
            # Test at a timestamp during the uptrend
            test_timestamp = datetime(2023, 1, 1, 10, 0)  # 10 AM
            
            timestamp_data = backtester._get_data_for_timestamp(all_data, ['BTCUSDT'], ['1m'], test_timestamp)
            
            # Step 1: Generate signals
            signals = strategy.generate_signals(timestamp_data)
            print(f"🔧 Step 1 - Generated signals: {signals}")
            
            # Step 2: Check if we can execute trade
            signal_value = signals['BTCUSDT']['1m']
            print(f"🔧 Step 2 - Signal value: {signal_value}")
            
            if signal_value in ['BUY', 'SELL']:
                can_execute = backtester._can_execute_trade('BTCUSDT', signal_value, test_timestamp)
                print(f"🔧 Step 3 - Can execute {signal_value} trade: {can_execute}")
                
                if can_execute:
                    # Step 4: Execute trade
                    trade_result = backtester._execute_trade('BTCUSDT', signal_value, test_timestamp, timestamp_data)
                    print(f"🔧 Step 4 - Trade result: {trade_result}")
                    
                    if trade_result.get('executed', False):
                        print("✅ Manual trade execution test PASSED")
                    else:
                        print(f"⚠️ Trade execution failed: {trade_result.get('reason', 'Unknown')}")
                else:
                    print(f"⚠️ Cannot execute {signal_value} trade")
            else:
                print(f"⚠️ Signal is {signal_value}, not executing trade")
            
        except Exception as e:
            print(f"❌ Manual trade execution test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    print("🚀 Starting Detailed Trade Execution Debug Test")
    print("=" * 60)
    
    unittest.main(verbosity=2)