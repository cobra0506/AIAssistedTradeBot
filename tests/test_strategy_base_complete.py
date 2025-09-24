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
        assert position_weak <= position_size   # Weak signal = smaller position
        
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
        
        # Get initial state
        state = strategy.get_strategy_state()
        
        # Verify structure
        required_keys = ['name', 'balance', 'initial_balance', 'total_return', 
                        'open_positions', 'total_trades', 'symbols', 'timeframes', 'config']
        for key in required_keys:
            assert key in state
        
        # Verify values
        assert state['name'] == strategy.name
        assert state['balance'] == strategy.balance
        assert state['initial_balance'] == strategy.initial_balance
        assert state['total_return'] == 0.0  # No trades yet
        assert state['open_positions'] == 0
        assert state['total_trades'] == 0
        assert state['symbols'] == strategy.symbols
        assert state['timeframes'] == strategy.timeframes
        assert state['config'] == strategy.config
        
        # Test with modified state
        strategy.balance = 15000
        strategy.positions = {'BTCUSDT': {}}
        strategy.trades = [{}]
        
        updated_state = strategy.get_strategy_state()
        assert updated_state['balance'] == 15000
        assert updated_state['total_return'] == 0.5  # 50% return
        assert updated_state['open_positions'] == 1
        assert updated_state['total_trades'] == 1
        
        print("✅ Strategy state test passed")
    
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
        prices = pd.Series([44, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.85, 46.08, 45.89, 46.03, 46.83, 47.69, 46.49, 46.26])
        rsi = calculate_rsi(prices, period=14)
        
        # Verify RSI properties
        assert len(rsi) == len(prices)
        assert rsi.min() >= 0
        assert rsi.max() <= 100
        assert rsi.isna().sum() == 13  # First 13 values should be NaN
        
        # Verify last value is reasonable (should be around 60-70 for this data)
        assert not pd.isna(rsi.iloc[-1])
        assert 0 <= rsi.iloc[-1] <= 100
        
        print("✅ RSI calculation test passed")
    
    def test_calculate_sma(self):
        """Test SMA calculation"""
        print("\n=== Testing SMA Calculation ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import calculate_sma_func as calculate_sma
        
        # Create test data
        prices = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        sma = calculate_sma(prices, period=5)
        
        # Verify SMA properties
        assert len(sma) == len(prices)
        assert sma.isna().sum() == 4  # First 4 values should be NaN
        
        # Verify specific calculations
        expected_values = [np.nan, np.nan, np.nan, np.nan, 30, 40, 50, 60, 70, 80]
        for i in range(4, len(prices)):
            assert abs(sma.iloc[i] - expected_values[i]) < 0.001
        
        print("✅ SMA calculation test passed")

    def test_calculate_ema(self):
        """Test EMA calculation"""
        print("\n=== Testing EMA Calculation ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import calculate_ema_func as calculate_ema
        
        # Create test data
        prices = pd.Series([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        ema = calculate_ema(prices, period=5)
        
        # Verify EMA properties
        assert len(ema) == len(prices)
        assert ema.isna().sum() == 0  # EMA has no NaN values
        
        # Verify EMA is more responsive than SMA
        sma = calculate_sma_func(prices, period=5)
        assert abs(ema.iloc[4] - prices.iloc[4]) < abs(sma.iloc[4] - prices.iloc[4])
        
        # Verify EMA values are reasonable
        assert ema.iloc[-1] > ema.iloc[0]  # Should trend upward
        
        print("✅ EMA calculation test passed")

    def test_calculate_stochastic(self):
        """Test Stochastic Oscillator calculation"""
        print("\n=== Testing Stochastic Calculation ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import calculate_stochastic_func as calculate_stochastic
        
        # Create test data
        data = pd.DataFrame({
            'high': [15, 16, 17, 16, 15, 16, 17, 18, 19, 18],
            'low': [10, 11, 12, 11, 10, 11, 12, 13, 14, 13],
            'close': [12, 13, 14, 13, 12, 13, 14, 15, 16, 15]
        })
        
        k_percent, d_percent = calculate_stochastic(data, k_period=5, d_period=3)
        
        # Verify Stochastic properties
        assert len(k_percent) == len(data)
        assert len(d_percent) == len(data)
        assert k_percent.min() >= 0
        assert k_percent.max() <= 100
        assert d_percent.min() >= 0
        assert d_percent.max() <= 100
        
        # Verify NaN values for warm-up period
        assert k_percent.isna().sum() == 4  # First 4 values should be NaN
        assert d_percent.isna().sum() == 6  # First 6 values should be NaN (5+3-1-1)
        
        print("✅ Stochastic calculation test passed")

    def test_calculate_srsi(self):
        """Test Stochastic RSI calculation"""
        print("\n=== Testing SRSI Calculation ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import calculate_srsi_func as calculate_srsi
        
        # Create test data
        prices = pd.Series([44, 44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.85, 46.08, 45.89, 46.03, 46.83, 47.69, 46.49, 46.26])
        srsi = calculate_srsi(prices, period=14)
        
        # Verify SRSI properties
        assert len(srsi) == len(prices)
        assert srsi.min() >= 0
        assert srsi.max() <= 100
        
        # Verify NaN values for warm-up period
        assert srsi.isna().sum() > 0  # Should have NaN values at start
        
        print("✅ SRSI calculation test passed")

class TestSignalBuildingBlocks:
    """Test signal building block functions"""
    
    def test_check_oversold(self):
        """Test oversold detection"""
        print("\n=== Testing Oversold Detection ===")
        
        # Use imported function
        from simple_strategy.shared.strategy_base import check_oversold
        
        # Create test indicator values
        indicator = pd.Series([15, 25, 35, 45, 55, 65, 75, 85])
        oversold = check_oversold(indicator, threshold=20)
        
        # Verify results
        expected = [True, False, False, False, False, False, False, False]
        pd.testing.assert_series_equal(oversold, pd.Series(expected))
        
        # Test custom threshold
        oversold_custom = check_oversold(indicator, threshold=30)
        expected_custom = [True, True, False, False, False, False, False, False]
        pd.testing.assert_series_equal(oversold_custom, pd.Series(expected_custom))
        
        print("✅ Oversold detection test passed")
    
    def test_check_overbought(self):
        """Test overbought detection"""
        print("\n=== Testing Overbought Detection ===")
        
        # Use imported function
        from simple_strategy.shared.strategy_base import check_overbought
        
        # Create test indicator values
        indicator = pd.Series([15, 25, 35, 45, 55, 65, 75, 85])
        overbought = check_overbought(indicator, threshold=80)
        
        # Verify results
        expected = [False, False, False, False, False, False, False, True]
        pd.testing.assert_series_equal(overbought, pd.Series(expected))
        
        # Test custom threshold
        overbought_custom = check_overbought(indicator, threshold=70)
        expected_custom = [False, False, False, False, False, False, True, True]
        pd.testing.assert_series_equal(overbought_custom, pd.Series(expected_custom))
        
        print("✅ Overbought detection test passed")
    
    def test_check_crossover(self):
        """Test crossover detection"""
        print("\n=== Testing Crossover Detection ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import check_crossover
        
        # Create test data with known crossover
        fast_ma = pd.Series([10, 12, 14, 16, 18, 20, 22, 24, 26, 28])
        slow_ma = pd.Series([15, 15, 15, 15, 15, 15, 15, 15, 15, 15])
        
        crossover = check_crossover(fast_ma, slow_ma)
        
        # Verify properties
        assert len(crossover) == len(fast_ma)
        assert crossover.iloc[0] is False  # First value can't be crossover
        
        # Find crossover point (when fast crosses above slow)
        # Should happen when fast goes from below to above slow
        crossover_points = crossover[crossover].index.tolist()
        assert len(crossover_points) >= 1  # Should have at least one crossover
        
        print("✅ Crossover detection test passed")

    def test_check_crossunder(self):
        """Test crossunder detection"""
        print("\n=== Testing Crossunder Detection ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import check_crossunder
        
        # Create test data with known crossunder
        fast_ma = pd.Series([20, 18, 16, 14, 12, 10, 8, 6, 4, 2])
        slow_ma = pd.Series([15, 15, 15, 15, 15, 15, 15, 15, 15, 15])
        
        crossunder = check_crossunder(fast_ma, slow_ma)
        
        # Verify properties
        assert len(crossunder) == len(fast_ma)
        assert crossunder.iloc[0] is False  # First value can't be crossunder
        
        # Find crossunder point (when fast crosses below slow)
        crossunder_points = crossunder[crossunder].index.tolist()
        assert len(crossunder_points) >= 1  # Should have at least one crossunder
        
        print("✅ Crossunder detection test passed")

class TestMultiTimeframeFunctions:
    """Test multi-timeframe functions"""
    
    def test_align_multi_timeframe_data(self):
        """Test multi-timeframe data alignment"""
        print("\n=== Testing Multi-Timeframe Data Alignment ===")
        
        # Use imported function (now renamed)
        from simple_strategy.shared.strategy_base import align_multi_timeframe_data
        
        # Create test data for different timeframes
        base_time = datetime(2024, 1, 1, 10, 0)
        
        # 1-minute data
        data_1m = pd.DataFrame({
            'timestamp': [int((base_time + timedelta(minutes=i)).timestamp() * 1000) for i in range(20)],
            'close': [50000 + i * 10 for i in range(20)]
        })
        
        # 5-minute data
        data_5m = pd.DataFrame({
            'timestamp': [int((base_time + timedelta(minutes=i*5)).timestamp() * 1000) for i in range(4)],
            'close': [50000 + i * 50 for i in range(4)]
        })
        
        # 15-minute data
        data_15m = pd.DataFrame({
            'timestamp': [int((base_time + timedelta(minutes=i*15)).timestamp() * 1000) for i in range(2)],
            'close': [50000 + i * 150 for i in range(2)]
        })
        
        # Test alignment
        target_timestamp = base_time + timedelta(minutes=7)  # 7 minutes after base
        aligned = align_multi_timeframe_data(data_1m, data_5m, data_15m, target_timestamp)
        
        # Verify alignment
        assert '1m' in aligned
        assert '5m' in aligned
        assert '15m' in aligned
        
        # Verify timestamps are close to target
        for tf, data_point in aligned.items():
            time_diff = abs(data_point['timestamp'] - int(target_timestamp.timestamp() * 1000))
            max_diff = {'1m': 30000, '5m': 150000, '15m': 450000}  # Half period in milliseconds
            assert time_diff <= max_diff[tf]
        
        print("✅ Multi-timeframe data alignment test passed")

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
    total = len(test_results)
    
    for result in test_results:
        print(result)
    
    print(f"\n📈 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL STRATEGY BASE TESTS PASSED!")
        print("✅ Strategy Base Component is working 100%")
        print("✅ Ready for strategy development and backtesting")
        print("✅ Phase 1.2 is COMPLETE and TESTED")
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
        print("❌ Strategy Base Component needs fixes")
    
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_strategy_tests()
    sys.exit(0 if success else 1)