import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import strategy functions
from simple_strategy.strategies.Strategy_1_Trend_Following import create_trend_following_strategy
from simple_strategy.strategies.Strategy_2_mean_reversion import create_mean_reversion_strategy
from simple_strategy.strategies.Strategy_3_Multi_Indicator import create_multi_indicator_strategy

# Import other required modules
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.backtester.backtester_engine import BacktesterEngine

class StrategyTestCase(unittest.TestCase):
    """Base test case for strategy testing"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = self.generate_test_data()
        self.start_date = '2023-01-01'
        self.end_date = '2023-12-31'
        self.initial_capital = 10000
    
    def generate_test_data(self):
        """Generate realistic test data for strategy validation"""
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='1h')
        n_periods = len(dates)
        
        # Generate realistic price movements
        np.random.seed(42)  # For reproducible tests
        returns = np.random.normal(0.0001, 0.02, n_periods)  # 0.01% mean, 2% std
        price = 100 * np.exp(np.cumsum(returns))  # Start at $100
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': price * (1 + np.random.normal(0, 0.001, n_periods)),
            'high': price * (1 + abs(np.random.normal(0, 0.005, n_periods))),
            'low': price * (1 - abs(np.random.normal(0, 0.005, n_periods))),
            'close': price,
            'volume': np.random.lognormal(10, 1, n_periods)
        })
        
        return data

class TestTrendFollowingStrategy(StrategyTestCase):
    """Test cases for Trend-Following Strategy"""
    
    def test_strategy_creation(self):
        """Test strategy can be created without errors"""
        strategy = create_trend_following_strategy()
        self.assertIsNotNone(strategy)
        self.assertEqual(len(strategy.symbols), 1)  # Default BTCUSDT
        self.assertEqual(len(strategy.timeframes), 2)  # 1h and 4h
    
    def test_indicator_calculation(self):
        """Test indicators are calculated correctly"""
        strategy = create_trend_following_strategy()
        
        # Test EMA calculations
        ema_fast = strategy.calculate_indicator('ema_fast', self.test_data)
        ema_slow = strategy.calculate_indicator('ema_slow', self.test_data)
        
        self.assertEqual(len(ema_fast), len(self.test_data))
        self.assertEqual(len(ema_slow), len(self.test_data))
        
        # EMA fast should be more responsive than EMA slow
        volatility_fast = np.std(ema_fast.pct_change().dropna())
        volatility_slow = np.std(ema_slow.pct_change().dropna())
        self.assertGreater(volatility_fast, volatility_slow)
    
    def test_signal_generation(self):
        """Test signals are generated according to strategy logic"""
        strategy = create_trend_following_strategy()
        signals = strategy.generate_signals(self.test_data)
        
        # Should have signals for most data points
        self.assertGreater(len(signals), len(self.test_data) * 0.8)
        
        # Signals should be -1, 0, or 1
        unique_signals = set(signals['signal'].unique())
        self.assertTrue(unique_signals.issubset({-1, 0, 1}))
    
    def test_backtest_integration(self):
        """Test strategy works with backtest engine"""
        from simple_strategy.backtester.backtester_engine import BacktesterEngine
        
        strategy = create_trend_following_strategy()
        backtest = BacktesterEngine(
            strategy=strategy,
            start_date=self.start_date,
            end_date=self.end_date,
            initial_capital=self.initial_capital
        )
        
        results = backtest.run()
        
        # Should return expected metrics
        expected_keys = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'total_trades']
        for key in expected_keys:
            self.assertIn(key, results)

class TestMeanReversionStrategy(StrategyTestCase):
    """Test cases for Mean Reversion Strategy"""
    
    def test_rsi_signals(self):
        """Test RSI-based overbought/oversold signals"""
        strategy = create_mean_reversion_strategy()
        signals = strategy.generate_signals(self.test_data)
        
        # Should generate both buy and sell signals
        buy_signals = signals[signals['signal'] == 1]
        sell_signals = signals[signals['signal'] == -1]
        
        self.assertGreater(len(buy_signals), 0)
        self.assertGreater(len(sell_signals), 0)
    
    def test_bollinger_bands_integration(self):
        """Test Bollinger Bands signals work correctly"""
        strategy = create_mean_reversion_strategy()
        
        # Calculate Bollinger Bands
        bb_upper = strategy.calculate_indicator('bb_upper', self.test_data)
        bb_lower = strategy.calculate_indicator('bb_lower', self.test_data)
        
        # Price should be within bands most of the time
        price = self.test_data['close']
        within_bands = ((price >= bb_lower) & (price <= bb_upper)).sum()
        within_bands_pct = within_bands / len(price)
        
        # Should be within bands ~95% of the time (2 standard deviations)
        self.assertGreater(within_bands_pct, 0.90)
        self.assertLess(within_bands_pct, 0.99)

class TestMultiIndicatorStrategy(StrategyTestCase):
    """Test cases for Multi-Indicator Strategy"""
    
    def test_signal_consensus(self):
        """Test that multiple indicators provide consensus"""
        strategy = create_multi_indicator_strategy()
        signals = strategy.generate_signals(self.test_data)
        
        # Should have fewer signals due to consensus requirement
        non_zero_signals = signals[signals['signal'] != 0]
        total_signals = len(signals)
        signal_ratio = len(non_zero_signals) / total_signals
        
        # Should have less than 50% active signals due to strict consensus
        self.assertLess(signal_ratio, 0.5)
    
    def test_multi_symbol_support(self):
        """Test strategy works with multiple symbols"""
        symbols = ['BTCUSDT', 'ETHUSDT']
        strategy = create_multi_indicator_strategy(symbols=symbols)
        
        self.assertEqual(len(strategy.symbols), 2)
        self.assertIn('BTCUSDT', strategy.symbols)
        self.assertIn('ETHUSDT', strategy.symbols)

def run_strategy_tests():
    """Run all strategy tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestTrendFollowingStrategy))
    suite.addTest(unittest.makeSuite(TestMeanReversionStrategy))
    suite.addTest(unittest.makeSuite(TestMultiIndicatorStrategy))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

# Run the tests
if __name__ == '__main__':
    run_strategy_tests()