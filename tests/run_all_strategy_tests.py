import sys
import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile
import shutil

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import strategy functions
from simple_strategy.strategies.Strategy_1_Trend_Following import create_trend_following_strategy
from simple_strategy.strategies.Strategy_2_mean_reversion import create_mean_reversion_strategy
from simple_strategy.strategies.Strategy_3_Multi_Indicator import create_multi_indicator_strategy

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

class SimpleStrategyTest(unittest.TestCase):
    """Simple test class to verify strategies work"""
    
    def setUp(self):
        """Set up test data and temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.initial_capital = 10000
        self._create_test_data()
    
    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_data(self):
        """Create test data files for backtesting"""
        # Create test data for BTCUSDT
        dates = pd.date_range(start='2023-01-01', end='2023-01-10', freq='1m')
        n_periods = len(dates)
        
        np.random.seed(42)
        returns = np.random.normal(0.0001, 0.02, n_periods)
        price = 100 * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': price * (1 + np.random.normal(0, 0.001, n_periods)),
            'high': price * (1 + abs(np.random.normal(0, 0.005, n_periods))),
            'low': price * (1 - abs(np.random.normal(0, 0.005, n_periods))),
            'close': price,
            'volume': np.random.lognormal(10, 1, n_periods)
        })
        
        # Create the correct directory structure
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Save 1m data directly in temp directory
        data_1m = data.copy()
        data_1m.to_csv(os.path.join(self.temp_dir, 'BTCUSDT_1m.csv'), index=False)
        
        # Create 1h data (resample from 1m)
        data_1h = data.set_index('timestamp').resample('1H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna().reset_index()
        data_1h.to_csv(os.path.join(self.temp_dir, 'BTCUSDT_1h.csv'), index=False)
        
        # Create 2h data (resample from 1m)
        data_2h = data.set_index('timestamp').resample('2H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna().reset_index()
        data_2h.to_csv(os.path.join(self.temp_dir, 'BTCUSDT_2h.csv'), index=False)
        
        # Create 4h data (resample from 1m)
        data_4h = data.set_index('timestamp').resample('4H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna().reset_index()
        data_4h.to_csv(os.path.join(self.temp_dir, 'BTCUSDT_4h.csv'), index=False)
        
        print(f"✅ Created test data in: {self.temp_dir}")
        print(f"   Files created: BTCUSDT_1m.csv, BTCUSDT_1h.csv, BTCUSDT_2h.csv, BTCUSDT_4h.csv")
    
    def test_trend_following_strategy(self):
        """Test trend following strategy"""
        print("Testing Trend Following Strategy...")
        
        try:
            # Create strategy
            strategy = create_trend_following_strategy()
            print("✅ Strategy created successfully")
            
            # Initialize components
            data_feeder = DataFeeder(data_dir=self.temp_dir)
            risk_manager = RiskManager(max_risk_per_trade=0.02, max_portfolio_risk=0.10)
            
            # Create backtester
            backtester = BacktesterEngine(
                data_feeder=data_feeder,
                strategy=strategy,
                risk_manager=risk_manager,
                config={"processing_mode": "sequential"}
            )
            print("✅ BacktesterEngine created successfully")
            
            # Run backtest
            results = backtester.run_backtest(
                symbols=['BTCUSDT'],
                timeframes=['1h', '4h'],
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 1, 10)
            )
            print(f"✅ Backtest completed: {results}")
            
        except Exception as e:
            print(f"❌ Error in trend following strategy: {e}")
            self.fail(f"Trend following strategy failed: {e}")
    
    def test_mean_reversion_strategy(self):
        """Test mean reversion strategy"""
        print("Testing Mean Reversion Strategy...")
        
        try:
            # Create strategy
            strategy = create_mean_reversion_strategy()
            print("✅ Strategy created successfully")
            
            # Initialize components
            data_feeder = DataFeeder(data_dir=self.temp_dir)
            risk_manager = RiskManager(max_risk_per_trade=0.02, max_portfolio_risk=0.10)
            
            # Create backtester
            backtester = BacktesterEngine(
                data_feeder=data_feeder,
                strategy=strategy,
                risk_manager=risk_manager,
                config={"processing_mode": "sequential"}
            )
            print("✅ BacktesterEngine created successfully")
            
            # Run backtest
            results = backtester.run_backtest(
                symbols=['BTCUSDT'],
                timeframes=['1h', '2h'],
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 1, 10)
            )
            print(f"✅ Backtest completed: {results}")
            
        except Exception as e:
            print(f"❌ Error in mean reversion strategy: {e}")
            self.fail(f"Mean reversion strategy failed: {e}")
    
    def test_multi_indicator_strategy(self):
        """Test multi indicator strategy"""
        print("Testing Multi Indicator Strategy...")
        
        try:
            # Create strategy
            strategy = create_multi_indicator_strategy()
            print("✅ Strategy created successfully")
            
            # Initialize components
            data_feeder = DataFeeder(data_dir=self.temp_dir)
            risk_manager = RiskManager(max_risk_per_trade=0.02, max_portfolio_risk=0.10)
            
            # Create backtester
            backtester = BacktesterEngine(
                data_feeder=data_feeder,
                strategy=strategy,
                risk_manager=risk_manager,
                config={"processing_mode": "sequential"}
            )
            print("✅ BacktesterEngine created successfully")
            
            # Run backtest
            results = backtester.run_backtest(
                symbols=['BTCUSDT'],
                timeframes=['1h', '4h'],
                start_date=datetime(2023, 1, 1),
                end_date=datetime(2023, 1, 10)
            )
            print(f"✅ Backtest completed: {results}")
            
        except Exception as e:
            print(f"❌ Error in multi indicator strategy: {e}")
            self.fail(f"Multi indicator strategy failed: {e}")

def run_simple_tests():
    """Run simple tests to verify everything works"""
    print("🚀 Running Simple Strategy Tests")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestSuite()
    suite.addTest(SimpleStrategyTest('test_trend_following_strategy'))
    suite.addTest(SimpleStrategyTest('test_mean_reversion_strategy'))
    suite.addTest(SimpleStrategyTest('test_multi_indicator_strategy'))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_simple_tests()