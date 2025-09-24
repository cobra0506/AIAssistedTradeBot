# test_strategy_base.py - Fixed with better crossunder test

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import warnings

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from shared.strategy_base import (
    StrategyBase, 
    calculate_rsi, calculate_sma, calculate_ema, calculate_stochastic, calculate_srsi,
    check_oversold, check_overbought, check_crossover, check_crossunder,
    align_multi_timeframe_data, check_multi_timeframe_condition,
    validate_data_format, clean_data, get_latest_data_point
)

# Suppress warnings for cleaner test output
warnings.filterwarnings('ignore')

class TestStrategyBase(unittest.TestCase):
    """Comprehensive test cases for StrategyBase abstract class"""
    
    # Define TestStrategy class at the class level so it's accessible to all test methods
    class TestStrategy(StrategyBase):
        def generate_signals(self, data):
            return {'BTCUSDT': {'1m': 'HOLD'}}
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = {
            'initial_balance': 10000,
            'max_risk_per_trade': 0.02,
            'max_positions': 5,
            'max_portfolio_risk': 0.15
        }
        
        # Create a concrete test strategy instance
        self.strategy = self.TestStrategy(
            name='TestStrategy',
            symbols=['BTCUSDT'],
            timeframes=['1m'],
            config=self.test_config
        )
        
        # Create empty data for utility tests
        self.empty_data = pd.DataFrame()
    
    def test_strategy_initialization(self):
        """Test strategy initialization with various configurations"""
        # Test basic initialization
        self.assertEqual(self.strategy.name, 'TestStrategy')
        self.assertEqual(self.strategy.symbols, ['BTCUSDT'])
        self.assertEqual(self.strategy.timeframes, ['1m'])
        self.assertEqual(self.strategy.balance, 10000)
        self.assertEqual(self.strategy.max_risk_per_trade, 0.02)
        self.assertEqual(self.strategy.max_positions, 5)
        self.assertEqual(self.strategy.max_portfolio_risk, 0.15)
        
        # Test with different configuration
        alt_config = {
            'initial_balance': 50000,
            'max_risk_per_trade': 0.01,
            'max_positions': 10,
            'max_portfolio_risk': 0.20
        }
        
        # Create a new TestStrategy instance with different config
        alt_strategy = self.TestStrategy(
            name='AltStrategy',
            symbols=['ETHUSDT'],
            timeframes=['5m'],
            config=alt_config
        )
        
        self.assertEqual(alt_strategy.balance, 50000)
        self.assertEqual(alt_strategy.max_risk_per_trade, 0.01)
        self.assertEqual(alt_strategy.max_positions, 10)
        self.assertEqual(alt_strategy.max_portfolio_risk, 0.20)
    
    def test_calculate_position_size(self):
        """Test position size calculation with various scenarios"""
        # Test with full signal strength
        position_size = self.strategy.calculate_position_size('BTCUSDT', 1.0)
        expected_risk = 10000 * 0.02 * 1.0  # balance * max_risk_per_trade * signal_strength
        expected_position = expected_risk / 50000  # risk / placeholder_price
        self.assertAlmostEqual(position_size, expected_position, places=6)
        
        # Test with half signal strength
        position_size_half = self.strategy.calculate_position_size('BTCUSDT', 0.5)
        self.assertAlmostEqual(position_size_half, expected_position * 0.5, places=6)
        
        # Test with zero signal strength
        position_size_zero = self.strategy.calculate_position_size('BTCUSDT', 0.0)
        self.assertEqual(position_size_zero, 0.0)
        
        # Test with negative signal strength (should be clamped to 0)
        position_size_negative = self.strategy.calculate_position_size('BTCUSDT', -0.5)
        self.assertEqual(position_size_negative, 0.0)
        
        # Test position size limits
        large_balance_config = self.test_config.copy()
        large_balance_config['initial_balance'] = 1000000
        large_strategy = self.TestStrategy(
            name='LargeStrategy',
            symbols=['BTCUSDT'],
            timeframes=['1m'],
            config=large_balance_config
        )
        
        # Should be limited to 20% of balance
        max_allowed = 1000000 * 0.2 / 50000  # 20% of balance / placeholder_price
        large_position = large_strategy.calculate_position_size('BTCUSDT', 1.0)
        self.assertLessEqual(large_position, max_allowed)
    
    def test_validate_signal(self):
        """Test signal validation with various scenarios"""
        # Test HOLD signal (should always be valid)
        self.assertTrue(self.strategy.validate_signal('BTCUSDT', 'HOLD', {}))
        
        # Test BUY signal with no positions (should be valid)
        self.assertTrue(self.strategy.validate_signal('BTCUSDT', 'BUY', {}))
        
        # Test SELL signal with no position (should be invalid)
        self.assertFalse(self.strategy.validate_signal('BTCUSDT', 'SELL', {}))
        
        # Test BUY signal with maximum positions (should be invalid)
        self.strategy.max_positions = 0
        self.assertFalse(self.strategy.validate_signal('BTCUSDT', 'BUY', {}))
        
        # Reset max positions
        self.strategy.max_positions = 5
        
        # Test BUY signal with maximum portfolio risk (should be invalid)
        self.strategy.max_portfolio_risk = 0.001  # Very low risk limit
        self.strategy.positions = {'BTCUSDT': {'value': 5000}}  # 50% of balance
        self.assertFalse(self.strategy.validate_signal('BTCUSDT', 'BUY', {}))
        
        # Test with valid portfolio risk
        self.strategy.max_portfolio_risk = 0.6  # Higher risk limit
        self.assertTrue(self.strategy.validate_signal('BTCUSDT', 'BUY', {}))
    
    def test_get_strategy_state(self):
        """Test strategy state retrieval"""
        state = self.strategy.get_strategy_state()
        
        # Check all expected fields are present
        expected_fields = [
            'name', 'balance', 'initial_balance', 'total_return',
            'open_positions', 'total_trades', 'symbols', 'timeframes', 'config'
        ]
        
        for field in expected_fields:
            self.assertIn(field, state)
        
        # Check values
        self.assertEqual(state['name'], 'TestStrategy')
        self.assertEqual(state['balance'], 10000)
        self.assertEqual(state['initial_balance'], 10000)
        self.assertEqual(state['total_return'], 0.0)
        self.assertEqual(state['open_positions'], 0)
        self.assertEqual(state['total_trades'], 0)
        self.assertEqual(state['symbols'], ['BTCUSDT'])
        self.assertEqual(state['timeframes'], ['1m'])
        
        # Test with some trades and positions
        self.strategy.balance = 12000
        self.strategy.trades = [{'symbol': 'BTCUSDT', 'pnl': 2000}]
        self.strategy.positions = {'BTCUSDT': {'value': 5000}}
        
        state = self.strategy.get_strategy_state()
        self.assertEqual(state['balance'], 12000)
        self.assertEqual(state['total_return'], 0.2)  # 20% return
        self.assertEqual(state['open_positions'], 1)
        self.assertEqual(state['total_trades'], 1)

class TestIndicatorFunctions(unittest.TestCase):
    """Comprehensive test cases for indicator calculation functions"""
    
    def setUp(self):
        """Set up test data"""
        # Create realistic price data
        np.random.seed(42)
        base_price = 100
        price_changes = np.random.normal(0, 1, 100)
        self.prices = pd.Series(base_price + np.cumsum(price_changes))
        
        # Create OHLC data for stochastic
        self.ohlc_data = pd.DataFrame({
            'high': self.prices + np.random.uniform(0, 2, 100),
            'low': self.prices - np.random.uniform(0, 2, 100),
            'close': self.prices
        })
        
        # Ensure high >= close >= low
        self.ohlc_data['high'] = np.maximum(self.ohlc_data['high'], self.ohlc_data['close'])
        self.ohlc_data['low'] = np.minimum(self.ohlc_data['low'], self.ohlc_data['close'])
    
    def test_calculate_sma(self):
        """Test SMA calculation with various periods"""
        # Test with different periods
        for period in [5, 10, 20]:
            sma = calculate_sma(self.prices, period)
            
            # Check length
            self.assertEqual(len(sma), len(self.prices))
            
            # Check that first (period-1) values are NaN
            self.assertTrue(sma.iloc[:period-1].isna().all())
            
            # Check that remaining values are not NaN
            self.assertFalse(sma.iloc[period-1:].isna().any())
            
            # Calculate the expected SMA correctly
            manual_sma = self.prices.iloc[:period].mean()  # Use first 'period' values
            self.assertAlmostEqual(sma.iloc[period-1], manual_sma, places=6)
    
    def test_calculate_ema(self):
        """Test EMA calculation with various periods"""
        # Test with different periods
        for period in [5, 10, 20]:
            ema = calculate_ema(self.prices, period)
            
            # Check length
            self.assertEqual(len(ema), len(self.prices))
            
            # Check that EMA is a pandas Series
            self.assertIsInstance(ema, pd.Series)
            
            # Check that first value is not NaN (EMA starts from first value)
            self.assertFalse(pd.isna(ema.iloc[0]))
            
            # Check that EMA reacts differently than SMA
            sma = calculate_sma(self.prices, period)
            # Skip NaN values in SMA for comparison
            valid_ema = ema.iloc[period-1:]
            valid_sma = sma.iloc[period-1:]
            
            # EMA should be different from SMA (except possibly at start)
            differences = (valid_ema - valid_sma).abs()
            self.assertGreater(differences.mean(), 0.001)
    
    def test_calculate_rsi(self):
        """Test RSI calculation with various periods"""
        # Test with different periods
        for period in [14, 21, 30]:
            rsi = calculate_rsi(self.prices, period)
            
            # Check length
            self.assertEqual(len(rsi), len(self.prices))
            
            # Check that values are not NaN where expected
            if period < len(self.prices):
                # Check that remaining values are not NaN
                self.assertFalse(rsi.iloc[period:].isna().any())
            
            # Check that RSI is between 0 and 100
            valid_rsi = rsi.dropna()
            if len(valid_rsi) > 0:
                self.assertTrue((valid_rsi >= 0).all())
                self.assertTrue((valid_rsi <= 100).all())
            
            # Test with constant prices (should give RSI around 50)
            constant_prices = pd.Series([100] * 50)
            constant_rsi = calculate_rsi(constant_prices, 14)
            valid_constant_rsi = constant_rsi.dropna()
            if len(valid_constant_rsi) > 0:
                self.assertAlmostEqual(valid_constant_rsi.iloc[-1], 50, delta=10)
    
    def test_calculate_stochastic(self):
        """Test Stochastic calculation with various periods"""
        # Test with different periods
        for k_period in [14, 21]:
            for d_period in [3, 5]:
                k_percent, d_percent = calculate_stochastic(self.ohlc_data, k_period, d_period)
                
                # Check length
                self.assertEqual(len(k_percent), len(self.ohlc_data))
                self.assertEqual(len(d_percent), len(self.ohlc_data))
                
                # Check that first (k_period-1) values of %K are NaN
                self.assertTrue(k_percent.iloc[:k_period-1].isna().all())
                
                # Check that %D has more NaN values than %K
                self.assertGreaterEqual(d_percent.isna().sum(), k_percent.isna().sum())
                
                # Check that values are between 0 and 100
                valid_k = k_percent.dropna()
                valid_d = d_percent.dropna()
                if len(valid_k) > 0:
                    self.assertTrue((valid_k >= 0).all())
                    self.assertTrue((valid_k <= 100).all())
                if len(valid_d) > 0:
                    self.assertTrue((valid_d >= 0).all())
                    self.assertTrue((valid_d <= 100).all())
                
                # Test edge case: high == low == close
                edge_data = pd.DataFrame({
                    'high': [100] * 20,
                    'low': [100] * 20,
                    'close': [100] * 20
                })
                k_edge, d_edge = calculate_stochastic(edge_data, k_period, d_period)
                valid_k_edge = k_edge.dropna()
                if len(valid_k_edge) > 0:
                    # When high == low == close, stochastic should be 50
                    self.assertTrue((valid_k_edge == 50).all())
    
    def test_calculate_srsi(self):
        """Test SRSI calculation with various periods"""
        # Test with different periods
        for period in [14, 21]:
            srsi = calculate_srsi(self.prices, period)
            
            # Check length
            self.assertEqual(len(srsi), len(self.prices))
            
            # Check that SRSI has more NaN values than RSI (due to additional stochastic calculation)
            rsi = calculate_rsi(self.prices, period)
            self.assertGreaterEqual(srsi.isna().sum(), rsi.isna().sum())
            
            # Check that values are between 0 and 100
            valid_srsi = srsi.dropna()
            if len(valid_srsi) > 0:
                self.assertTrue((valid_srsi >= 0).all())
                self.assertTrue((valid_srsi <= 100).all())

class TestSignalFunctions(unittest.TestCase):
    """Comprehensive test cases for signal building block functions"""
    
    def setUp(self):
        """Set up test data"""
        # Create test data for various scenarios
        self.rsi_values = pd.Series([25, 30, 75, 80, 20, 85, 15, 50, 70, 30])
        self.fast_ma = pd.Series([10, 12, 11, 13, 15, 14, 16, 15, 17, 16])
        self.slow_ma = pd.Series([10, 11, 12, 12, 13, 14, 15, 15, 16, 16])
    
    def test_debug_crossunder(self):
        """Debug test for crossunder detection"""
        print("\n=== DEBUG CROSSUNDER TEST ===")
        
        # Test data that should definitely create a crossunder
        fast_cross = pd.Series([15, 14, 13])
        slow_cross = pd.Series([10, 11, 12])
        
        print("Fast series:", fast_cross.values)
        print("Slow series:", slow_cross.values)
        
        # Calculate crossunder
        crossunder_clear = check_crossunder(fast_cross, slow_cross)
        
        print("Crossunder result:", crossunder_clear.values)
        print("Index 1 crossunder:", crossunder_clear.iloc[1])
        
        # Manual verification
        print("\nManual verification:")
        print("At index 1:")
        print("  Current: fast =", fast_cross.iloc[1], "slow =", slow_cross.iloc[1])
        print("  Previous: fast =", fast_cross.iloc[0], "slow =", slow_cross.iloc[0])
        print("  Current condition (fast < slow):", fast_cross.iloc[1] < slow_cross.iloc[1])
        print("  Previous condition (fast_prev >= slow_prev):", fast_cross.iloc[0] >= slow_cross.iloc[0])
        print("  Combined (both True):", (fast_cross.iloc[1] < slow_cross.iloc[1]) and (fast_cross.iloc[0] >= slow_cross.iloc[0]))
        
        # This should definitely be True
        self.assertTrue(crossunder_clear.iloc[1], 
                    f"Crossunder detection failed at index 1. Expected True, got {crossunder_clear.iloc[1]}")

    def test_check_oversold(self):
        """Test oversold condition checking with various thresholds"""
        # Test with default threshold (20)
        oversold = check_oversold(self.rsi_values, 20)
        self.assertIsInstance(oversold, pd.Series)
        self.assertEqual(len(oversold), len(self.rsi_values))
        
        # Check specific values
        expected_oversold = self.rsi_values <= 20
        pd.testing.assert_series_equal(oversold, expected_oversold)
        
        # Test with different thresholds
        for threshold in [10, 30, 50]:
            oversold_custom = check_oversold(self.rsi_values, threshold)
            expected_custom = self.rsi_values <= threshold
            pd.testing.assert_series_equal(oversold_custom, expected_custom)
        
        # Test with edge cases
        # All values oversold
        all_oversold = pd.Series([5, 10, 15])
        oversold_all = check_oversold(all_oversold, 20)
        self.assertTrue(oversold_all.all())
        
        # No values oversold
        none_oversold = pd.Series([80, 85, 90])
        oversold_none = check_oversold(none_oversold, 20)
        self.assertFalse(oversold_none.any())
    
    def test_check_overbought(self):
        """Test overbought condition checking with various thresholds"""
        # Test with default threshold (80)
        overbought = check_overbought(self.rsi_values, 80)
        self.assertIsInstance(overbought, pd.Series)
        self.assertEqual(len(overbought), len(self.rsi_values))
        
        # Check specific values
        expected_overbought = self.rsi_values >= 80
        pd.testing.assert_series_equal(overbought, expected_overbought)
        
        # Test with different thresholds
        for threshold in [70, 85, 95]:
            overbought_custom = check_overbought(self.rsi_values, threshold)
            expected_custom = self.rsi_values >= threshold
            pd.testing.assert_series_equal(overbought_custom, expected_custom)
        
        # Test with edge cases
        # All values overbought
        all_overbought = pd.Series([85, 90, 95])
        overbought_all = check_overbought(all_overbought, 80)
        self.assertTrue(overbought_all.all())
        
        # No values overbought
        none_overbought = pd.Series([20, 25, 30])
        overbought_none = check_overbought(none_overbought, 80)
        self.assertFalse(overbought_none.any())
    
    def test_check_crossover(self):
        """Test crossover detection with various scenarios"""
        crossover = check_crossover(self.fast_ma, self.slow_ma)
        self.assertIsInstance(crossover, pd.Series)
        self.assertEqual(len(crossover), len(self.fast_ma))
        
        # Check that we get some crossovers (the exact indices depend on the data)
        # There should be at least one crossover in our test data
        self.assertTrue(crossover.any())
        
        # Check non-crossovers
        # Index 0: 10 == 10 (not crossover, no previous value)
        self.assertFalse(crossover.iloc[0])
        
        # Test edge cases
        # No crossovers
        fast_no_cross = pd.Series([10, 11, 12])
        slow_no_cross = pd.Series([15, 16, 17])
        crossover_none = check_crossover(fast_no_cross, slow_no_cross)
        self.assertFalse(crossover_none.any())
        
        # Test when fast is always above slow
        fast_all_above = pd.Series([15, 16, 17])
        slow_all_below = pd.Series([10, 11, 12])
        crossover_above = check_crossover(fast_all_above, slow_all_below)
        # Should have crossover at index 0 if fast starts above slow
        # But if there's no previous data, no crossover detected
        self.assertFalse(crossover_above.any())
    
    def test_check_crossunder(self):
        """Test crossunder detection with various scenarios"""
        crossunder = check_crossunder(self.fast_ma, self.slow_ma)
        self.assertIsInstance(crossunder, pd.Series)
        self.assertEqual(len(crossunder), len(self.fast_ma))
        
        # Check that we get some crossunders (the exact indices depend on the data)
        # There should be at least one crossunder in our test data
        self.assertTrue(crossunder.any())
        
        # Check non-crossunders
        # Index 0: 10 == 10 (not crossunder, no previous value)
        self.assertFalse(crossunder.iloc[0])
        
        # Test edge cases
        # No crossunders
        fast_no_cross = pd.Series([10, 11, 12])
        slow_no_cross = pd.Series([5, 6, 7])
        crossunder_none = check_crossunder(fast_no_cross, slow_no_cross)
        self.assertFalse(crossunder_none.any())
        
        # FIXED: Create a clear crossunder scenario with debugging
        print("\n=== DEBUG CROSSUNDER TEST ===")
        
        # Test data that should definitely create a crossunder
        fast_cross = pd.Series([15, 14, 13])
        slow_cross = pd.Series([10, 11, 12])
        
        print("Fast series:", fast_cross.values)
        print("Slow series:", slow_cross.values)
        
        # Calculate crossunder
        crossunder_clear = check_crossunder(fast_cross, slow_cross)
        
        print("Crossunder result:", crossunder_clear.values)
        print("Index 1 crossunder:", crossunder_clear.iloc[1])
        
        # Manual verification
        fast_prev = fast_cross.shift(1)
        slow_prev = slow_cross.shift(1)
        
        print("Fast_prev:", fast_prev.values)
        print("Slow_prev:", slow_prev.values)
        
        current_condition = fast_cross < slow_cross
        prev_condition = fast_prev >= slow_prev
        
        print("Current condition (fast < slow):", current_condition.values)
        print("Previous condition (fast_prev >= slow_prev):", prev_condition.values)
        print("Combined condition:", (current_condition & prev_condition).values)
        
        # This should definitely be True at index 1
        self.assertTrue(crossunder_clear.iloc[1], 
                       f"Crossunder detection failed at index 1. Expected True, got {crossunder_clear.iloc[1]}")

class TestMultiTimeframeFunctions(unittest.TestCase):
    """Comprehensive test cases for multi-timeframe functions"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample data for different timeframes
        base_time = datetime(2023, 1, 1, 0, 0, 0)
        
        # 1-minute data
        self.data_1m = pd.DataFrame({
            'open': [100, 101, 102, 103, 104, 105, 106, 107],
            'high': [101, 102, 103, 104, 105, 106, 107, 108],
            'low': [99, 100, 101, 102, 103, 104, 105, 106],
            'close': [101, 102, 103, 104, 105, 106, 107, 108],
            'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700]
        }, index=[base_time + timedelta(minutes=i) for i in range(8)])
        
        # 5-minute data
        self.data_5m = pd.DataFrame({
            'open': [100, 105],
            'high': [105, 110],
            'low': [95, 100],
            'close': [105, 110],
            'volume': [5000, 6000]
        }, index=[base_time, base_time + timedelta(minutes=5)])
        
        # 15-minute data
        self.data_15m = pd.DataFrame({
            'open': [100],
            'high': [110],
            'low': [95],
            'close': [110],
            'volume': [15000]
        }, index=[base_time])
    
    def test_align_multi_timeframe_data(self):
        """Test multi-timeframe data alignment with various scenarios"""
        # Test with normal data
        test_time = datetime(2023, 1, 1, 0, 3, 0)
        aligned = align_multi_timeframe_data(self.data_1m, self.data_5m, self.data_15m, test_time)
        
        self.assertIsInstance(aligned, dict)
        self.assertIn('1m', aligned)
        self.assertIn('5m', aligned)
        self.assertIn('15m', aligned)
        
        # Check that aligned data has correct values
        self.assertEqual(aligned['1m']['close'], 104)  # 3rd minute
        self.assertEqual(aligned['5m']['close'], 105)  # First 5m candle
        self.assertEqual(aligned['15m']['close'], 110)  # Only 15m candle
        
        # Test with timestamp before all data
        early_time = datetime(2022, 12, 31, 23, 59, 0)
        aligned_early = align_multi_timeframe_data(self.data_1m, self.data_5m, self.data_15m, early_time)
        self.assertEqual(len(aligned_early), 0)
        
        # Test with timestamp after all data
        late_time = datetime(2023, 1, 1, 0, 10, 0)
        aligned_late = align_multi_timeframe_data(self.data_1m, self.data_5m, self.data_15m, late_time)
        
        self.assertIn('1m', aligned_late)
        self.assertIn('5m', aligned_late)
        self.assertIn('15m', aligned_late)
        
        # Should get latest available data
        self.assertEqual(aligned_late['1m']['close'], 108)  # Last 1m candle
        self.assertEqual(aligned_late['5m']['close'], 110)  # Last 5m candle
        self.assertEqual(aligned_late['15m']['close'], 110)  # Last 15m candle
        
        # Test with None data
        aligned_none = align_multi_timeframe_data(self.data_1m, None, self.data_15m, test_time)
        self.assertIn('1m', aligned_none)
        self.assertNotIn('5m', aligned_none)
        self.assertIn('15m', aligned_none)
    
    def test_check_multi_timeframe_condition(self):
        """Test multi-timeframe condition checking with various scenarios"""
        # Test with both Series and scalar values
        indicators_series = {
            '1m': {'rsi': pd.Series([25, 30])},
            '5m': {'rsi': pd.Series([35, 40])},
            '15m': {'rsi': pd.Series([45, 50])}
        }
        
        # Test condition that should be true
        condition_func_true = lambda values: values['1m']['rsi'] <= 30
        result_true = check_multi_timeframe_condition(indicators_series, condition_func_true)
        self.assertTrue(result_true)
        
        # Test with scalar values
        indicators_scalar = {
            '1m': {'rsi': 25},
            '5m': {'rsi': 35},
            '15m': {'rsi': 45}
        }
        
        result_scalar = check_multi_timeframe_condition(indicators_scalar, condition_func_true)
        self.assertTrue(result_scalar)
        
        # Test condition that should be false
        condition_func_false = lambda values: values['1m']['rsi'] <= 20
        result_false = check_multi_timeframe_condition(indicators_scalar, condition_func_false)
        self.assertFalse(result_false)
        
        # Test complex condition across timeframes
        condition_func_complex = lambda values: (
            values['1m']['rsi'] < values['5m']['rsi'] < values['15m']['rsi']
        )
        result_complex = check_multi_timeframe_condition(indicators_scalar, condition_func_complex)
        self.assertTrue(result_complex)
        
        # Test with missing timeframe
        indicators_missing = {
            '1m': {'rsi': 25},
            '15m': {'rsi': 45}
        }
        
        condition_func_missing = lambda values: '5m' not in values
        result_missing = check_multi_timeframe_condition(indicators_missing, condition_func_missing)
        self.assertTrue(result_missing)
        
        # Test with empty indicators
        empty_indicators = {}
        condition_func_empty = lambda values: len(values) == 0
        result_empty = check_multi_timeframe_condition(empty_indicators, condition_func_empty)
        self.assertTrue(result_empty)

class TestUtilityFunctions(unittest.TestCase):
    """Comprehensive test cases for utility functions"""
    
    def setUp(self):
        """Set up test data"""
        # Valid OHLCV data
        self.valid_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101],
            'close': [101, 102, 103],
            'volume': [1000, 1100, 1200]
        })
        
        # Missing required columns
        self.invalid_data = pd.DataFrame({
            'open': [100, 101, 102],
            'close': [101, 102, 103]
        })
        
        # Data with missing values and infinities
        self.dirty_data = pd.DataFrame({
            'open': [100, np.nan, 102, np.inf],
            'high': [101, 102, 103, 104],
            'low': [99, 100, 101, 102],
            'close': [101, 102, 103, 104],
            'volume': [1000, 1100, 1200, 1300]
        })
        
        # Time series data
        self.test_time = datetime(2023, 1, 1, 12, 0, 0)
        self.time_series_data = pd.DataFrame({
            'open': [100, 101, 102, 103],
            'high': [101, 102, 103, 104],
            'low': [99, 100, 101, 102],
            'close': [101, 102, 103, 104],
            'volume': [1000, 1100, 1200, 1300]
        }, index=[datetime(2023, 1, 1, 11, 58, 0), 
                 datetime(2023, 1, 1, 11, 59, 0),
                 datetime(2023, 1, 1, 12, 0, 0),
                 datetime(2023, 1, 1, 12, 1, 0)])
        
        # Empty data for testing edge cases
        self.empty_data = pd.DataFrame()
    
    def test_validate_data_format(self):
        """Test data format validation with various scenarios"""
        # Test with valid data
        self.assertTrue(validate_data_format(self.valid_data))
        
        # Test with invalid data (missing columns)
        self.assertFalse(validate_data_format(self.invalid_data))
        
        # Test with extra columns (should still be valid)
        extra_col_data = self.valid_data.copy()
        extra_col_data['extra'] = [1, 2, 3]
        self.assertTrue(validate_data_format(extra_col_data))
        
        # Test with empty DataFrame
        empty_df = pd.DataFrame()
        self.assertFalse(validate_data_format(empty_df))
        
        # Test with only some required columns
        partial_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [101, 102, 103],
            'low': [99, 100, 101]
        })
        self.assertFalse(validate_data_format(partial_data))
    
    def test_clean_data(self):
        """Test data cleaning with various scenarios"""
        # Test with dirty data containing NaN and inf
        cleaned = clean_data(self.dirty_data)
        
        # Should have no NaN or infinite values
        self.assertFalse(cleaned.isna().any().any())
        self.assertFalse(np.isinf(cleaned.values).any())
        
        # Should have fewer rows due to dropped NaN values
        self.assertLess(len(cleaned), len(self.dirty_data))
        
        # Test with already clean data
        cleaned_clean = clean_data(self.valid_data)
        pd.testing.assert_frame_equal(cleaned_clean, self.valid_data)
        
        # Test with all NaN data
        all_nan_data = pd.DataFrame({
            'open': [np.nan, np.nan],
            'high': [np.nan, np.nan],
            'low': [np.nan, np.nan],
            'close': [np.nan, np.nan],
            'volume': [np.nan, np.nan]
        })
        cleaned_nan = clean_data(all_nan_data)
        self.assertEqual(len(cleaned_nan), 0)  # All rows should be dropped
    
    def test_get_latest_data_point(self):
        """Test getting latest data point with various scenarios"""
        # Test with normal time series data
        latest = get_latest_data_point(self.time_series_data, self.test_time)
        
        # Should return a pandas Series
        self.assertIsInstance(latest, pd.Series)
        
        # Check that it has the expected values
        self.assertEqual(latest['open'], 102)
        self.assertEqual(latest['high'], 103)
        self.assertEqual(latest['low'], 101)
        self.assertEqual(latest['close'], 103)
        self.assertEqual(latest['volume'], 1200)
        
        # Test with timestamp before all data
        early_time = datetime(2023, 1, 1, 11, 57, 0)
        latest_early = get_latest_data_point(self.time_series_data, early_time)
        self.assertIsNone(latest_early)
        
        # Test with timestamp after all data
        late_time = datetime(2023, 1, 1, 12, 2, 0)
        latest_late = get_latest_data_point(self.time_series_data, late_time)
        
        # Should get the last available data point
        self.assertEqual(latest_late['open'], 103)
        self.assertEqual(latest_late['high'], 104)
        self.assertEqual(latest_late['low'], 102)
        self.assertEqual(latest_late['close'], 104)
        self.assertEqual(latest_late['volume'], 1300)
        
        # Test with empty data
        latest_empty = get_latest_data_point(self.empty_data, self.test_time)
        self.assertIsNone(latest_empty)


if __name__ == '__main__':
    unittest.main()