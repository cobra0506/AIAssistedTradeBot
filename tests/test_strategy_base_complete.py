# test_strategy_base_complete.py - CONSOLIDATED VERSION
import pytest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from abc import ABC, abstractmethod

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the StrategyBase and functions from the correct location
from simple_strategy.shared.strategy_base import (
    StrategyBase,
    calculate_rsi_func as calculate_rsi,
    calculate_sma_func as calculate_sma,
    calculate_ema_func as calculate_ema,
    calculate_stochastic_func as calculate_stochastic,
    calculate_srsi_func as calculate_srsi,
    check_oversold,
    check_overbought,
    check_crossover,
    check_crossunder,
    align_multi_timeframe_data
)

class TestStrategy(StrategyBase):
    """Concrete test strategy implementation"""
    def generate_signals(self, data):
        """Simple test strategy - buy when RSI < 30, sell when RSI > 70"""
        signals = {}
        for symbol, timeframe_data in data.items():
            signals[symbol] = {}
            for timeframe, df in timeframe_data.items():
                if 'close' in df.columns and len(df) > 14:
                    # Calculate RSI using the method (which now uses calculate_rsi_func)
                    rsi = self.calculate_rsi(df['close'], period=14)
                    if not pd.isna(rsi.iloc[-1]):
                        if rsi.iloc[-1] < 30:
                            signals[symbol][timeframe] = 'BUY'
                        elif rsi.iloc[-1] > 70:
                            signals[symbol][timeframe] = 'SELL'
                        else:
                            signals[symbol][timeframe] = 'HOLD'
                    else:
                        signals[symbol][timeframe] = 'HOLD'
                else:
                    signals[symbol][timeframe] = 'HOLD'
        return signals

class TestStrategyBase:
    """Comprehensive test suite for StrategyBase component"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            'initial_balance': 10000,
            'max_risk_per_trade': 0.02,
            'max_positions': 3,
            'max_portfolio_risk': 0.10
        }
    
    @pytest.fixture
    def strategy(self, config):
        """Create a concrete strategy for testing"""
        return TestStrategy(
            name='TestStrategy',
            symbols=['BTCUSDT', 'ETHUSDT'],
            timeframes=['1m', '5m'],
            config=config
        )
    
    @pytest.fixture
    def sample_data(self):
        """Create sample market data for testing"""
        # Create sample price data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1min')
        data = {}
        for symbol in ['BTCUSDT', 'ETHUSDT']:
            # Generate realistic price data
            base_price = 50000 if symbol == 'BTCUSDT' else 3000
            prices = []
            current_price = base_price
            for i in range(len(dates)):
                # Random walk with slight upward bias
                change = np.random.normal(0, 0.001)  # 0.1% std deviation
                current_price *= (1 + change)
                prices.append(current_price)
            df = pd.DataFrame({
                'timestamp': [int(d.timestamp() * 1000) for d in dates],
                'datetime': dates,
                'open': prices,
                'high': [p * 1.002 for p in prices],  # High slightly above open
                'low': [p * 0.998 for p in prices],   # Low slightly below open
                'close': prices,
                'volume': [np.random.uniform(100, 1000) for _ in prices]
            })
            data[symbol] = df
        return data

    def create_multi_timeframe_data(self):
        """Create multi-timeframe data for testing (regular function, not fixture)"""
        base_time = datetime(2024, 1, 1, 10, 0)
        # Create nested structure: {symbol: {timeframe: DataFrame}}
        data = {}
        for symbol in ['BTCUSDT']:
            data[symbol] = {}
            # 1-minute data
            dates_1m = pd.date_range(start=base_time, periods=100, freq='1min')
            prices_1m = [50000 + i * 10 for i in range(100)]
            data[symbol]['1m'] = pd.DataFrame({
                'timestamp': [int(d.timestamp() * 1000) for d in dates_1m],
                'open': prices_1m,
                'high': [p * 1.002 for p in prices_1m],
                'low': [p * 0.998 for p in prices_1m],
                'close': prices_1m,
                'volume': [1000] * 100
            })
            # 5-minute data
            dates_5m = pd.date_range(start=base_time, periods=20, freq='5min')
            prices_5m = [50000 + i * 50 for i in range(20)]
            data[symbol]['5m'] = pd.DataFrame({
                'timestamp': [int(d.timestamp() * 1000) for d in dates_5m],
                'open': prices_5m,
                'high': [p * 1.002 for p in prices_5m],
                'low': [p * 0.998 for p in prices_5m],
                'close': prices_5m,
                'volume': [5000] * 20
            })
            # 15-minute data
            dates_15m = pd.date_range(start=base_time, periods=7, freq='15min')
            prices_15m = [50000 + i * 150 for i in range(7)]
            data[symbol]['15m'] = pd.DataFrame({
                'timestamp': [int(d.timestamp() * 1000) for d in dates_15m],
                'open': prices_15m,
                'high': [p * 1.002 for p in prices_15m],
                'low': [p * 0.998 for p in prices_15m],
                'close': prices_15m,
                'volume': [15000] * 7
            })
        return data

    def test_strategy_base_initialization(self, strategy, config):
        """Test base class initialization"""
        print("\n=== Testing Strategy Base Initialization ===")
        # Test basic attributes
        assert strategy.name == 'TestStrategy'
        assert strategy.symbols == ['BTCUSDT', 'ETHUSDT']
        assert strategy.timeframes == ['1m', '5m']
        assert strategy.config == config
        assert strategy.balance == config['initial_balance']
        assert strategy.initial_balance == strategy.balance
        assert strategy.positions == {}
        assert strategy.trades == []
        assert strategy.equity_curve == []
        # Test risk management parameters
        assert strategy.max_risk_per_trade == config['max_risk_per_trade']
        assert strategy.max_positions == config['max_positions']
        assert strategy.max_portfolio_risk == config['max_portfolio_risk']
        print("✅ Strategy base initialization test passed")

    def test_calculate_position_size(self, strategy):
        """Test position sizing calculations"""
        print("\n=== Testing Position Sizing Calculations ===")
        # Test with default signal strength
        position_size = strategy.calculate_position_size('BTCUSDT', signal_strength=1.0)
        # Verify calculation
        expected_risk_amount = strategy.balance * strategy.max_risk_per_trade
        expected_position_size = expected_risk_amount / 50000  # Placeholder price
        assert position_size > 0
        assert position_size <= strategy.balance * 0.2  # Max 20% limit
        # Test with different signal strengths
        position_strong = strategy.calculate_position_size('BTCUSDT', signal_strength=2.0)
        position_weak = strategy.calculate_position_size('BTCUSDT', signal_strength=0.5)
        assert position_strong >= position_size  # Strong signal = larger position
        assert position_weak <= position_size  # Weak signal = smaller position
        # Test negative signal strength (should be clamped to 0)
        position_negative = strategy.calculate_position_size('BTCUSDT', signal_strength=-1.0)
        assert position_negative >= 0
        print("✅ Position sizing calculations test passed")

    def test_validate_signal(self, strategy):
        """Test signal validation against risk management rules"""
        print("\n=== Testing Signal Validation ===")
        # Test HOLD signal (should always be valid)
        assert strategy.validate_signal('BTCUSDT', 'HOLD', {}) is True
        # Test valid BUY signals
        assert strategy.validate_signal('BTCUSDT', 'BUY', {}) is True
        # Test maximum positions limit
        strategy.positions = {'ETHUSDT': {}, 'SOLUSDT': {}, 'ADAUSDT': {}}  # 3 positions
        assert strategy.validate_signal('BTCUSDT', 'BUY', {}) is False  # Should reject
        # Reset positions
        strategy.positions = {}
        # Test portfolio risk limit
        with patch.object(strategy, '_calculate_portfolio_risk', return_value=0.15):  # 15% > 10% limit
            assert strategy.validate_signal('BTCUSDT', 'BUY', {}) is False
        # Test SELL signal without position
        assert strategy.validate_signal('BTCUSDT', 'SELL', {}) is False
        # Test SELL signal with position
        strategy.positions = {'BTCUSDT': {}}
        assert strategy.validate_signal('BTCUSDT', 'SELL', {}) is True
        print("✅ Signal validation test passed")

    def test_strategy_state(self, strategy):
        """Test strategy state retrieval"""
        print("\n=== Testing Strategy State ===")
        try:
            # Reset strategy state to ensure clean test
            strategy.balance = 10000  # Reset to initial balance
            strategy.positions = {}     # Clear any positions
            strategy.trades = []        # Clear any trades
            
            # Get initial state
            state = strategy.get_strategy_state()
            print(f"Initial state: {state}")
            
            # Verify structure
            required_keys = ['name', 'balance', 'initial_balance', 'total_return',
                            'open_positions', 'total_trades', 'symbols', 'timeframes', 'config']
            for key in required_keys:
                assert key in state, f"Missing key: {key}"
            
            # Verify values
            assert state['name'] == strategy.name, f"Name mismatch: {state['name']} != {strategy.name}"
            assert state['balance'] == strategy.balance, f"Balance mismatch: {state['balance']} != {strategy.balance}"
            assert state['initial_balance'] == strategy.initial_balance, f"Initial balance mismatch: {state['initial_balance']} != {strategy.initial_balance}"
            assert state['total_return'] == 0.0, f"Total return mismatch: {state['total_return']} != 0.0"
            assert state['open_positions'] == 0, f"Open positions mismatch: {state['open_positions']} != 0"
            assert state['total_trades'] == 0, f"Total trades mismatch: {state['total_trades']} != 0"
            assert state['symbols'] == strategy.symbols, f"Symbols mismatch: {state['symbols']} != {strategy.symbols}"
            assert state['timeframes'] == strategy.timeframes, f"Timeframes mismatch: {state['timeframes']} != {strategy.timeframes}"
            assert state['config'] == strategy.config, f"Config mismatch: {state['config']} != {strategy.config}"
            
            # Test with modified state
            strategy.balance = 15000
            strategy.positions = {'BTCUSDT': {}}
            strategy.trades = [{}]
            updated_state = strategy.get_strategy_state()
            print(f"Updated state: {updated_state}")
            
            assert updated_state['balance'] == 15000, f"Updated balance mismatch: {updated_state['balance']} != 15000"
            
            # Check total return with tolerance for floating point precision
            expected_return = 0.5  # 50% return
            actual_return = updated_state['total_return']
            assert abs(actual_return - expected_return) < 0.001, f"Total return mismatch: {actual_return} != {expected_return}"
            
            assert updated_state['open_positions'] == 1, f"Updated open positions mismatch: {updated_state['open_positions']} != 1"
            assert updated_state['total_trades'] == 1, f"Updated total trades mismatch: {updated_state['total_trades']} != 1"
            
            print("✅ Strategy state test passed")
        except Exception as e:
            print(f"❌ Strategy state test failed with exception: {e}")
            raise

    def test_generate_signals(self, strategy):
        """Test signal generation"""
        print("\n=== Testing Signal Generation ===")
        # Create multi-timeframe data using the regular function
        multi_timeframe_data = self.create_multi_timeframe_data()
        # Generate signals
        signals = strategy.generate_signals(multi_timeframe_data)
        # Verify structure
        assert isinstance(signals, dict)
        assert 'BTCUSDT' in signals
        # Verify signal values
        for symbol, timeframe_signals in signals.items():
            assert isinstance(timeframe_signals, dict)
            for timeframe, signal in timeframe_signals.items():
                assert signal in ['BUY', 'SELL', 'HOLD']
        print("✅ Signal generation test passed")

    def test_portfolio_risk_calculation(self, strategy):
        """Test portfolio risk calculation"""
        print("\n=== Testing Portfolio Risk Calculation ===")
        # Test with no positions
        risk = strategy._calculate_portfolio_risk()
        assert risk == 0.0
        # Test with positions
        strategy.positions = {
            'BTCUSDT': {'value': 2000},
            'ETHUSDT': {'value': 1000}
        }
        risk = strategy._calculate_portfolio_risk()
        expected_risk = 3000 / strategy.balance  # 3000 / 10000 = 0.3
        assert abs(risk - expected_risk) < 0.001
        print("✅ Portfolio risk calculation test passed")

class TestIndicatorBuildingBlocks:
    """Test indicator building block functions"""
    
    def test_calculate_rsi(self):
        """Test RSI calculation"""
        print("\n=== Testing RSI Calculation ===")
        # Create test data with known pattern
        prices = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128])
        # Calculate RSI
        rsi = calculate_rsi(prices, period=5)
        # Verify basic properties
        assert len(rsi) == len(prices)
        assert rsi.min() >= 0  # RSI should be between 0 and 100
        assert rsi.max() <= 100
        print("✅ RSI Calculation test passed")

    def test_calculate_sma(self):
        """Test SMA calculation"""
        print("\n=== Testing SMA Calculation ===")
        # Create test data
        prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
        # Calculate SMA
        sma = calculate_sma(prices, period=5)
        # Verify basic properties
        assert len(sma) == len(prices)
        assert sma.isna().sum() == 4  # First 4 values should be NaN for period=5
        # Verify calculation manually
        expected_sma = (105 + 106 + 107 + 108 + 109) / 5
        assert abs(sma.iloc[-1] - expected_sma) < 0.001
        print("✅ SMA Calculation test passed")

    def test_calculate_ema(self):
        """Test EMA calculation"""
        print("\n=== Testing EMA Calculation ===")
        # Create test data
        prices = pd.Series([100, 101, 102, 103, 104, 105, 106, 107, 108, 109])
        # Calculate EMA
        ema = calculate_ema(prices, period=5)
        # Verify basic properties
        assert len(ema) == len(prices)
        assert ema.isna().sum() == 0  # No NaN values
        # EMA should be more responsive than SMA
        sma = calculate_sma(prices, period=5)
        assert ema.iloc[-1] > sma.iloc[-1]  # EMA should be closer to current price
        # Test with different period
        ema_long = calculate_ema(prices, period=10)
        assert len(ema_long) == len(prices)
        print("✅ EMA Calculation test passed")

    def test_calculate_stochastic(self):
        """Test Stochastic calculation"""
        print("\n=== Testing Stochastic Calculation ===")
        # Create test data
        data = pd.DataFrame({
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [100, 101, 102, 103, 104]
        })
        # Calculate Stochastic
        k_percent, d_percent = calculate_stochastic(data, k_period=3, d_period=2)
        # Verify basic properties
        assert len(k_percent) == len(data)
        assert len(d_percent) == len(data)
        assert k_percent.min() >= 0  # Stochastic should be between 0 and 100
        assert k_percent.max() <= 100
        assert d_percent.min() >= 0
        assert d_percent.max() <= 100
        print("✅ Stochastic Calculation test passed")

    def test_calculate_srsi(self):
        """Test SRSI calculation"""
        print("\n=== Testing SRSI Calculation ===")
        # FIXED: Use more varied test data to get better SRSI values
        prices = pd.Series([100, 105, 95, 110, 90, 115, 85, 120, 80, 125, 75, 130, 70, 135, 65, 
                           140, 60, 145, 55, 150, 50, 155, 45, 160, 40, 165, 35, 170, 30, 175])
        # Calculate SRSI
        srsi = calculate_srsi(prices, period=5)
        # Verify basic properties
        assert len(srsi) == len(prices)
        # Check that non-NaN values are within expected range
        valid_srsi = srsi.dropna()
        assert len(valid_srsi) > 0  # Should have some valid values
        assert valid_srsi.min() >= 0  # SRSI should be between 0 and 100
        assert valid_srsi.max() <= 100
        # Test with different period
        srsi_long = calculate_srsi(prices, period=10)
        assert len(srsi_long) == len(prices)
        print("✅ SRSI Calculation test passed")

class TestSignalBuildingBlocks:
    """Test signal building block functions"""
    
    def test_check_oversold(self):
        """Test oversold detection"""
        print("\n=== Testing Oversold Detection ===")
        # Create test data
        rsi_values = pd.Series([25, 20, 15, 30, 35, 18, 22])
        # Check oversold conditions
        oversold = check_oversold(rsi_values, threshold=20)
        # Verify basic properties
        assert len(oversold) == len(rsi_values)
        assert oversold.dtype == bool
        # Should detect oversold at indices 1, 2, 5
        assert oversold.iloc[1] == True  # 20 <= 20
        assert oversold.iloc[2] == True  # 15 <= 20
        assert oversold.iloc[5] == True  # 18 <= 20
        assert oversold.iloc[0] == False  # 25 > 20
        print("✅ Oversold Detection test passed")
    
    def test_check_overbought(self):
        """Test overbought detection"""
        print("\n=== Testing Overbought Detection ===")
        # Create test data
        rsi_values = pd.Series([75, 80, 85, 70, 65, 82, 78])
        # Check overbought conditions
        overbought = check_overbought(rsi_values, threshold=80)
        # Verify basic properties
        assert len(overbought) == len(rsi_values)
        assert overbought.dtype == bool
        # Should detect overbought at indices 1, 2, 5
        assert overbought.iloc[1] == True  # 80 >= 80
        assert overbought.iloc[2] == True  # 85 >= 80
        assert overbought.iloc[5] == True  # 82 >= 80
        assert overbought.iloc[0] == False  # 75 < 80
        print("✅ Overbought Detection test passed")

    def test_check_crossover(self):
        """Test crossover detection"""
        print("\n=== Testing Crossover Detection ===")
        # Create test data with known crossover
        fast_ma = pd.Series([10, 11, 12, 13, 14, 16, 17, 18, 19, 20])
        slow_ma = pd.Series([15, 15, 15, 15, 15, 15, 15, 15, 15, 15])
        # Detect crossover
        crossover = check_crossover(fast_ma, slow_ma)
        # Verify basic properties
        assert len(crossover) == len(fast_ma)
        assert crossover.dtype == bool
        assert not crossover.iloc[0]  # First value should never be True
        # Should detect crossover at index 5
        assert crossover.iloc[5] == True
        print("✅ Crossover Detection test passed")

    def test_check_crossunder(self):
        """Test crossunder detection"""
        print("\n=== Testing Crossunder Detection ===")
        # Create test data with known crossunder
        fast_ma = pd.Series([20, 19, 18, 17, 16, 14, 13, 12, 11, 10])
        slow_ma = pd.Series([15, 15, 15, 15, 15, 15, 15, 15, 15, 15])
        # Detect crossunder
        crossunder = check_crossunder(fast_ma, slow_ma)
        # Verify basic properties
        assert len(crossunder) == len(fast_ma)
        assert crossunder.dtype == bool
        assert not crossunder.iloc[0]  # First value should never be True
        # Should detect crossunder at index 5
        assert crossunder.iloc[5] == True
        print("✅ Crossunder Detection test passed")

class TestMultiTimeframeFunctions:
    """Test multi-timeframe functionality"""
    
    def test_align_multi_timeframe_data(self):
        """Test multi-timeframe data alignment"""
        print("\n=== Testing Multi-Timeframe Data Alignment ===")
        # Create test data
        data_dict = {
            'BTCUSDT': {
                '1m': pd.DataFrame({
                    'timestamp': [1640995200000, 1640995260000],
                    'open': [50000, 50100],
                    'high': [50100, 50200],
                    'low': [49900, 50000],
                    'close': [50050, 50150],
                    'volume': [1000, 1100]
                }),
                '5m': pd.DataFrame({
                    'timestamp': [1640995200000, 1640995500000],
                    'open': [50000, 50200],
                    'high': [50200, 50300],
                    'low': [49800, 50100],
                    'close': [50100, 50250],
                    'volume': [5000, 5500]
                })
            }
        }
        # Align data
        aligned_data = align_multi_timeframe_data(data_dict)
        # Verify structure
        assert 'BTCUSDT' in aligned_data
        assert '1m' in aligned_data['BTCUSDT']
        assert '5m' in aligned_data['BTCUSDT']
        # Verify datetime conversion
        assert 'datetime' in aligned_data['BTCUSDT']['1m'].columns
        assert 'datetime' in aligned_data['BTCUSDT']['5m'].columns
        print("✅ Multi-Timeframe Data Alignment test passed")

def run_comprehensive_strategy_tests():
    """Run all strategy base tests"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE STRATEGY BASE TEST SUITE")
    print("=" * 80)
    
    # Create test instances
    config = {
        'initial_balance': 10000,
        'max_risk_per_trade': 0.02,
        'max_positions': 3,
        'max_portfolio_risk': 0.10
    }
    
    strategy = TestStrategy(
        name='TestStrategy',
        symbols=['BTCUSDT', 'ETHUSDT'],
        timeframes=['1m', '5m'],
        config=config
    )
    
    # Run all tests
    test_results = []
    
    try:
        test_suite = TestStrategyBase()
        test_suite.test_strategy_base_initialization(strategy, config)
        test_results.append("✅ Strategy Base Initialization")
    except Exception as e:
        test_results.append(f"❌ Strategy Base Initialization: {e}")
    
    try:
        test_suite.test_calculate_position_size(strategy)
        test_results.append("✅ Position Sizing Calculations")
    except Exception as e:
        test_results.append(f"❌ Position Sizing Calculations: {e}")
    
    try:
        test_suite.test_validate_signal(strategy)
        test_results.append("✅ Signal Validation")
    except Exception as e:
        test_results.append(f"❌ Signal Validation: {e}")
    
    try:
        test_suite.test_strategy_state(strategy)
        test_results.append("✅ Strategy State")
    except Exception as e:
        test_results.append(f"❌ Strategy State: {e}")
    
    try:
        test_suite.test_generate_signals(strategy)
        test_results.append("✅ Signal Generation")
    except Exception as e:
        test_results.append(f"❌ Signal Generation: {e}")
    
    try:
        test_suite.test_portfolio_risk_calculation(strategy)
        test_results.append("✅ Portfolio Risk Calculation")
    except Exception as e:
        test_results.append(f"❌ Portfolio Risk Calculation: {e}")
    
    try:
        TestIndicatorBuildingBlocks().test_calculate_rsi()
        test_results.append("✅ RSI Calculation")
    except Exception as e:
        test_results.append(f"❌ RSI Calculation: {e}")
    
    try:
        TestIndicatorBuildingBlocks().test_calculate_sma()
        test_results.append("✅ SMA Calculation")
    except Exception as e:
        test_results.append(f"❌ SMA Calculation: {e}")
    
    try:
        TestIndicatorBuildingBlocks().test_calculate_ema()
        test_results.append("✅ EMA Calculation")
    except Exception as e:
        test_results.append(f"❌ EMA Calculation: {e}")
    
    try:
        TestIndicatorBuildingBlocks().test_calculate_stochastic()
        test_results.append("✅ Stochastic Calculation")
    except Exception as e:
        test_results.append(f"❌ Stochastic Calculation: {e}")
    
    try:
        TestIndicatorBuildingBlocks().test_calculate_srsi()
        test_results.append("✅ SRSI Calculation")
    except Exception as e:
        test_results.append(f"❌ SRSI Calculation: {e}")
    
    try:
        TestSignalBuildingBlocks().test_check_oversold()
        test_results.append("✅ Oversold Detection")
    except Exception as e:
        test_results.append(f"❌ Oversold Detection: {e}")
    
    try:
        TestSignalBuildingBlocks().test_check_overbought()
        test_results.append("✅ Overbought Detection")
    except Exception as e:
        test_results.append(f"❌ Overbought Detection: {e}")
    
    try:
        TestSignalBuildingBlocks().test_check_crossover()
        test_results.append("✅ Crossover Detection")
    except Exception as e:
        test_results.append(f"❌ Crossover Detection: {e}")
    
    try:
        TestSignalBuildingBlocks().test_check_crossunder()
        test_results.append("✅ Crossunder Detection")
    except Exception as e:
        test_results.append(f"❌ Crossunder Detection: {e}")
    
    try:
        TestMultiTimeframeFunctions().test_align_multi_timeframe_data()
        test_results.append("✅ Multi-Timeframe Data Alignment")
    except Exception as e:
        test_results.append(f"❌ Multi-Timeframe Data Alignment: {e}")

    # Print results
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for result in test_results if result.startswith("✅"))
    failed = len(test_results) - passed
    
    for result in test_results:
        print(result)
    
    print(f"\n📈 Tests Passed: {passed}/{len(test_results)}")
    
    if failed > 0:
        print(f"⚠️  {failed} TESTS FAILED")
        print("❌ Strategy Base Component needs fixes")
    else:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Strategy Base Component is working correctly")
    
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_strategy_tests()