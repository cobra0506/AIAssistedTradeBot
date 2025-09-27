"""
Comprehensive Integration Test for Strategy Builder + Backtest Engine
Tests the complete workflow from strategy creation to backtest execution
"""
import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path
import sys
import logging

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.performance_tracker import PerformanceTracker
from simple_strategy.backtester.position_manager import PositionManager
from simple_strategy.shared.data_feeder import DataFeeder
from simple_strategy.shared.strategy_base import StrategyBase
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma, macd
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStrategyBuilderBacktestIntegration(unittest.TestCase):
    """Comprehensive test suite for Strategy Builder + Backtest Engine integration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        print("🔧 Setting up Strategy Builder + Backtest Engine integration test...")
        
    def setUp(self):
        """Set up test components"""
        print("🔧 Setting up test components...")
        try:
            # Create temporary directory for test data
            self.temp_dir = tempfile.mkdtemp()
            print(f"✅ Temp directory created: {self.temp_dir}")
            
            # Create test data
            self._create_test_data()
            print("✅ Test data created")
            
            # Initialize DataFeeder
            self.data_feeder = DataFeeder(data_dir=self.temp_dir)
            print("✅ DataFeeder initialized")
            
            # Initialize Risk Manager
            self.risk_manager = RiskManager(
                max_risk_per_trade=0.02,
                max_portfolio_risk=0.10,
                max_positions=3,
                default_stop_loss_pct=0.02
            )
            print("✅ RiskManager initialized")
            
            print("🔧 Setup completed successfully!")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            import shutil
            if hasattr(self, 'temp_dir'):
                shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up temp directory")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")
    
    def _create_test_data(self):
        """Create realistic test data for backtesting"""
        print("📝 Creating test data...")
        try:
            # Create timestamps for 5 days of 1-minute data
            start_time = datetime(2023, 1, 1, 0, 0)
            timestamps = []
            unix_timestamps = []
            
            for day in range(5):
                for minute in range(1440):  # 1440 minutes per day
                    dt = start_time + timedelta(days=day, minutes=minute)
                    timestamps.append(dt)
                    unix_timestamps.append(int(dt.timestamp() * 1000))
            
            print(f"✅ Created {len(timestamps)} timestamps")
            
            # Create price data with realistic patterns
            np.random.seed(42)
            for symbol in ["BTCUSDT", "ETHUSDT"]:
                print(f"📈 Creating data for {symbol}...")
                
                # Base prices
                if symbol == "BTCUSDT":
                    base_price = 20000.0
                    volatility = 0.015
                    trend = 0.0008
                else:
                    base_price = 1500.0
                    volatility = 0.02
                    trend = 0.001
                
                prices = []
                volumes = []
                
                for i, timestamp in enumerate(timestamps):
                    # Generate realistic price movement with some trends
                    daily_volatility = volatility / np.sqrt(1440)
                    
                    # Add some cyclical patterns
                    cycle_factor = 0.3 * np.sin(2 * np.pi * i / 1440)  # Daily cycle
                    trend_factor = trend * i / 1440  # Upward trend
                    random_factor = np.random.normal(0, daily_volatility)
                    
                    price = base_price * (1 + trend_factor + cycle_factor + random_factor)
                    prices.append(price)
                    volumes.append(np.random.randint(100, 1000))
                
                # Create DataFrame
                data = pd.DataFrame({
                    'timestamp': unix_timestamps,
                    'datetime': timestamps,
                    'open': prices,
                    'high': [p * 1.001 for p in prices],
                    'low': [p * 0.999 for p in prices],
                    'close': prices,
                    'volume': volumes
                })
                
                # Format datetime as string
                data['datetime'] = data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
                # Save to CSV
                csv_filename = f"{symbol}_1m.csv"
                csv_path = os.path.join(self.temp_dir, csv_filename)
                data.to_csv(csv_path, index=False)
                print(f"✅ Saved data for {symbol}")
                
        except Exception as e:
            print(f"❌ Error creating test data: {e}")
            raise
    
    def test_strategy_builder_basic_integration(self):
        """Test basic integration: Strategy Builder -> Backtest Engine"""
        print("🧪 Testing basic Strategy Builder integration...")
        
        try:
            # 1. Create a strategy using Strategy Builder
            print("📝 Step 1: Creating strategy with Strategy Builder...")
            strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
            
            # Add indicators
            strategy_builder.add_indicator('rsi', rsi, period=14)
            strategy_builder.add_indicator('sma_short', sma, period=20)
            strategy_builder.add_indicator('sma_long', sma, period=50)
            
            # Add signal rules
            strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                            indicator='rsi', overbought=70, oversold=30)
            strategy_builder.add_signal_rule('ma_cross', ma_crossover, 
                                            fast_ma='sma_short', slow_ma='sma_long')
            
            # Add risk rules
            strategy_builder.add_risk_rule('stop_loss', percent=2.0)
            strategy_builder.add_risk_rule('take_profit', percent=4.0)
            
            # Set signal combination
            strategy_builder.set_signal_combination('weighted', 
                                                  weights={'rsi_signal': 0.6, 'ma_cross': 0.4})
            
            # Build the strategy
            strategy = strategy_builder.build()
            print("✅ Strategy built successfully")
            
            # 2. Initialize backtest engine with the built strategy
            print("🔧 Step 2: Initializing backtest engine...")
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager,
                config={"processing_mode": "sequential"}
            )
            print("✅ Backtest engine initialized")
            
            # 3. Run the backtest
            print("🚀 Step 3: Running backtest...")
            symbols = ["BTCUSDT"]
            timeframes = ["1m"]
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2023, 1, 3)
            
            results = backtester.run_backtest(symbols, timeframes, start_date, end_date)
            print("✅ Backtest completed")
            
            # 4. Validate results
            print("🔍 Step 4: Validating results...")
            self.assertIsNotNone(results, "Results should not be None")
            self.assertNotIn('error', results, "Backtest should not have errors")
            
            # Check expected result keys
            expected_keys = ['equity_curve', 'trades', 'signals', 'timestamps', 'portfolio_values']
            for key in expected_keys:
                self.assertIn(key, results, f"Results should contain {key}")
            
            # Check that we have some trades
            self.assertGreater(len(results['trades']), 0, "Should have some trades")
            print(f"✅ Generated {len(results['trades'])} trades")
            
            # Check that equity curve exists
            self.assertGreater(len(results['equity_curve']), 0, "Should have equity curve data")
            print("✅ Equity curve generated")
            
            print("🎉 Basic integration test PASSED!")
            
        except Exception as e:
            print(f"❌ Basic integration test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_multi_symbol_strategy_integration(self):
        """Test multi-symbol strategy integration"""
        print("🧪 Testing multi-symbol strategy integration...")
        
        try:
            # 1. Create a multi-symbol strategy
            print("📝 Step 1: Creating multi-symbol strategy...")
            strategy_builder = StrategyBuilder(['BTCUSDT', 'ETHUSDT'], ['1m'])
            
            # Add indicators
            strategy_builder.add_indicator('rsi_btc', rsi, period=14)
            strategy_builder.add_indicator('rsi_eth', rsi, period=14)
            strategy_builder.add_indicator('sma_btc', sma, period=20)
            strategy_builder.add_indicator('sma_eth', sma, period=20)
            
            # Add signal rules
            strategy_builder.add_signal_rule('rsi_btc_signal', overbought_oversold, 
                                            indicator='rsi_btc', overbought=70, oversold=30)
            strategy_builder.add_signal_rule('rsi_eth_signal', overbought_oversold, 
                                            indicator='rsi_eth', overbought=70, oversold=30)
            
            # Add risk rules
            strategy_builder.add_risk_rule('stop_loss', percent=1.5)
            strategy_builder.add_risk_rule('take_profit', percent=3.0)
            
            # Set signal combination
            strategy_builder.set_signal_combination('majority_vote')
            
            # Build the strategy
            strategy = strategy_builder.build()
            print("✅ Multi-symbol strategy built successfully")
            
            # 2. Initialize and run backtest
            print("🔧 Step 2: Running multi-symbol backtest...")
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager,
                config={"processing_mode": "sequential"}
            )
            
            symbols = ["BTCUSDT", "ETHUSDT"]
            timeframes = ["1m"]
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2023, 1, 3)
            
            results = backtester.run_backtest(symbols, timeframes, start_date, end_date)
            print("✅ Multi-symbol backtest completed")
            
            # 3. Validate results
            print("🔍 Step 3: Validating multi-symbol results...")
            self.assertIsNotNone(results, "Results should not be None")
            self.assertNotIn('error', results, "Backtest should not have errors")
            
            # Check that we have trades for both symbols
            trades = results['trades']
            self.assertGreater(len(trades), 0, "Should have some trades")
            
            # Check that both symbols are represented in trades
            trade_symbols = set(trade.get('symbol', '') for trade in trades)
            self.assertTrue('BTCUSDT' in trade_symbols or 'ETHUSDT' in trade_symbols, 
                           "Should have trades for at least one symbol")
            
            print(f"✅ Generated {len(trades)} trades across symbols: {trade_symbols}")
            print("🎉 Multi-symbol integration test PASSED!")
            
        except Exception as e:
            print(f"❌ Multi-symbol integration test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_complex_strategy_integration(self):
        """Test complex strategy with multiple indicators and signals"""
        print("🧪 Testing complex strategy integration...")
        
        try:
            # 1. Create a complex strategy
            print("📝 Step 1: Creating complex strategy...")
            strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
            
            # Add multiple indicators
            strategy_builder.add_indicator('rsi', rsi, period=14)
            strategy_builder.add_indicator('sma_short', sma, period=10)
            strategy_builder.add_indicator('sma_long', sma, period=30)
            strategy_builder.add_indicator('macd', macd, fast_period=12, slow_period=26, signal_period=9)
            
            # Add multiple signal rules
            strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                            indicator='rsi', overbought=70, oversold=30)
            strategy_builder.add_signal_rule('ma_cross', ma_crossover, 
                                            fast_ma='sma_short', slow_ma='sma_long')
            
            # Add comprehensive risk rules
            strategy_builder.add_risk_rule('stop_loss', percent=1.0)
            strategy_builder.add_risk_rule('take_profit', percent=2.5)
            strategy_builder.add_risk_rule('max_position_size', percent=10.0)
            
            # Set weighted signal combination
            strategy_builder.set_signal_combination('weighted', 
                                                  weights={'rsi_signal': 0.7, 'ma_cross': 0.3})
            
            # Build the strategy
            strategy = strategy_builder.build()
            print("✅ Complex strategy built successfully")
            
            # 2. Initialize and run backtest
            print("🔧 Step 2: Running complex strategy backtest...")
            backtester = BacktesterEngine(
                data_feeder=self.data_feeder,
                strategy=strategy,
                risk_manager=self.risk_manager,
                config={"processing_mode": "sequential"}
            )
            
            symbols = ["BTCUSDT"]
            timeframes = ["1m"]
            start_date = datetime(2023, 1, 1)
            end_date = datetime(2023, 1, 4)  # Longer test period
            
            results = backtester.run_backtest(symbols, timeframes, start_date, end_date)
            print("✅ Complex strategy backtest completed")
            
            # 3. Validate results
            print("🔍 Step 3: Validating complex strategy results...")
            self.assertIsNotNone(results, "Results should not be None")
            self.assertNotIn('error', results, "Backtest should not have errors")
            
            # Check comprehensive results
            trades = results['trades']
            equity_curve = results['equity_curve']
            signals = results['signals']
            
            self.assertGreater(len(trades), 0, "Should have some trades")
            self.assertGreater(len(equity_curve), 0, "Should have equity curve data")
            self.assertGreater(len(signals), 0, "Should have signal data")
            
            # Check trade structure
            if trades:
                first_trade = trades[0]
                expected_trade_keys = ['symbol', 'timestamp', 'signal', 'price', 'quantity']
                for key in expected_trade_keys:
                    self.assertIn(key, first_trade, f"Trade should contain {key}")
            
            print(f"✅ Complex strategy results: {len(trades)} trades, {len(equity_curve)} equity points")
            print("🎉 Complex strategy integration test PASSED!")
            
        except Exception as e:
            print(f"❌ Complex strategy integration test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def test_error_handling_integration(self):
        """Test error handling in the integration"""
        print("🧪 Testing error handling integration...")
        
        try:
            # Test 1: Invalid strategy configuration
            print("📝 Test 1: Invalid strategy configuration...")
            try:
                strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
                # Try to build without adding indicators or signals
                strategy = strategy_builder.build()
                self.fail("Should have raised an error for empty strategy")
            except ValueError as e:
                print(f"✅ Correctly caught empty strategy error: {e}")
            
            # Test 2: Invalid signal combination
            print("📝 Test 2: Invalid signal combination...")
            try:
                strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy_builder.add_indicator('rsi', rsi, period=14)
                strategy_builder.add_signal_rule('rsi_signal', overbought_oversold, 
                                                indicator='rsi', overbought=70, oversold=30)
                # Try to set invalid combination method
                strategy_builder.set_signal_combination('invalid_method')
                self.fail("Should have raised an error for invalid combination method")
            except ValueError as e:
                print(f"✅ Correctly caught invalid combination method error: {e}")
            
            # Test 3: Invalid indicator reference
            print("📝 Test 3: Invalid indicator reference...")
            try:
                strategy_builder = StrategyBuilder(['BTCUSDT'], ['1m'])
                strategy_builder.add_indicator('rsi', rsi, period=14)
                # Try to reference non-existent indicator
                strategy_builder.add_signal_rule('bad_signal', overbought_oversold, 
                                                indicator='nonexistent', overbought=70, oversold=30)
                self.fail("Should have raised an error for invalid indicator reference")
            except ValueError as e:
                print(f"✅ Correctly caught invalid indicator reference error: {e}")
            
            print("🎉 Error handling integration test PASSED!")
            
        except Exception as e:
            print(f"❌ Error handling integration test failed: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    # Run the tests
    print("🚀 Starting Strategy Builder + Backtest Engine Integration Tests")
    print("=" * 60)
    
    unittest.main(verbosity=2)