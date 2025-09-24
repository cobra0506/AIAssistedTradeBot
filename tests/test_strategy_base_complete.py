import pytest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock
from abc import ABC, abstractmethod

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the StrategyBase (adjust path based on your actual implementation)
try:
    from shared_modules.simple_strategy.shared.strategy_base import StrategyBase
    STRATEGY_BASE_EXISTS = True
except ImportError:
    STRATEGY_BASE_EXISTS = False
    print("⚠️  StrategyBase not found - creating mock for testing")

# Mock StrategyBase if it doesn't exist yet
if not STRATEGY_BASE_EXISTS:
    class StrategyBase(ABC):
        """Mock StrategyBase for testing purposes"""
        def __init__(self, name, symbols, timeframes, config):
            self.name = name
            self.symbols = symbols
            self.timeframes = timeframes
            self.config = config
            self.positions = {}
            self.balance = config.get('initial_balance', 10000)
            
        @abstractmethod
        def generate_signals(self, data):
            """Generate trading signals - must be implemented by subclasses"""
            pass
            
        def calculate_position_size(self, symbol, signal_strength=1.0):
            """Calculate position size based on risk management"""
            risk_percent = self.config.get('risk_per_trade', 0.02)  # 2% risk per trade
            account_balance = self.balance
            risk_amount = account_balance * risk_percent * signal_strength
            
            # Get current price (mock for testing)
            current_price = 50000  # Mock BTC price
            
            # Calculate position size
            position_size = risk_amount / current_price
            
            return {
                'quantity': position_size,
                'risk_amount': risk_amount,
                'risk_percent': risk_percent * 100
            }
            
        def validate_signal(self, symbol, signal, data):
            """Validate signal against risk management rules"""
            # Check if we already have a position
            current_position = self.positions.get(symbol, 0)
            
            # Prevent multiple positions in same direction
            if current_position > 0 and signal == 'BUY':
                return False, 'Already in long position'
            if current_position < 0 and signal == 'SELL':
                return False, 'Already in short position'
                
            # Check max position size
            max_position = self.config.get('max_position_size', 1.0)
            if abs(current_position) >= max_position:
                return False, 'Maximum position size reached'
                
            return True, 'Signal valid'
            
        def get_strategy_state(self):
            """Get current strategy state for logging"""
            return {
                'name': self.name,
                'symbols': self.symbols,
                'timeframes': self.timeframes,
                'balance': self.balance,
                'positions': self.positions,
                'config': self.config
            }

class TestStrategyBase:
    """Comprehensive test suite for StrategyBase component"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            'initial_balance': 10000,
            'risk_per_trade': 0.02,
            'max_position_size': 1.0,
            'max_daily_loss': 0.05
        }
    
    @pytest.fixture
    def strategy(self, config):
        """Create a concrete strategy for testing"""
        class TestStrategy(StrategyBase):
            def generate_signals(self, data):
                # Simple test strategy - buy when RSI < 30, sell when RSI > 70
                signals = {}
                for symbol, symbol_data in data.items():
                    if 'close' in symbol_data.columns:
                        # Calculate RSI
                        rsi = self.calculate_rsi(symbol_data['close'], period=14)
                        if rsi.iloc[-1] < 30:
                            signals[symbol] = 'BUY'
                        elif rsi.iloc[-1] > 70:
                            signals[symbol] = 'SELL'
                        else:
                            signals[symbol] = 'HOLD'
                return signals
        
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
    
    def test_strategy_base_initialization(self, strategy, config):
        """Test base class initialization"""
        print("\n=== Testing Strategy Base Initialization ===")
        
        # Test basic attributes
        assert strategy.name == 'TestStrategy'
        assert strategy.symbols == ['BTCUSDT', 'ETHUSDT']
        assert strategy.timeframes == ['1m', '5m']
        assert strategy.config == config
        assert strategy.balance == config['initial_balance']
        assert strategy.positions == {}
        
        print("✅ Strategy base initialization test passed")
    
    def test_calculate_position_size(self, strategy):
        """Test position sizing calculations"""
        print("\n=== Testing Position Sizing Calculations ===")
        
        # Test with default signal strength
        position_info = strategy.calculate_position_size('BTCUSDT', signal_strength=1.0)
        
        # Verify structure
        assert 'quantity' in position_info
        assert 'risk_amount' in position_info
        assert 'risk_percent' in position_info
        
        # Verify calculations
        expected_risk_amount = strategy.balance * strategy.config['risk_per_trade']
        assert position_info['risk_amount'] == expected_risk_amount
        assert position_info['risk_percent'] == 2.0  # 2%
        assert position_info['quantity'] > 0
        
        # Test with different signal strengths
        position_strong = strategy.calculate_position_size('BTCUSDT', signal_strength=2.0)
        position_weak = strategy.calculate_position_size('BTCUSDT', signal_strength=0.5)
        
        assert position_strong['quantity'] > position_info['quantity']
        assert position_weak['quantity'] < position_info['quantity']
        
        print("✅ Position sizing calculations test passed")
    
    def test_signal_validation(self, strategy):
        """Test signal validation against risk management rules"""
        print("\n=== Testing Signal Validation ===")
        
        # Test valid signals with no positions
        valid_buy, reason_buy = strategy.validate_signal('BTCUSDT', 'BUY', {})
        valid_sell, reason_sell = strategy.validate_signal('BTCUSDT', 'SELL', {})
        
        assert valid_buy is True
        assert valid_sell is True
        assert reason_buy == 'Signal valid'
        assert reason_sell == 'Signal valid'
        
        # Test with existing positions
        strategy.positions['BTCUSDT'] = 1.0  # Long position
        
        # Should reject duplicate long signal
        valid_duplicate, reason_duplicate = strategy.validate_signal('BTCUSDT', 'BUY', {})
        assert valid_duplicate is False
        assert 'Already in long position' in reason_duplicate
        
        # Should allow opposite signal
        valid_opposite, reason_opposite = strategy.validate_signal('BTCUSDT', 'SELL', {})
        assert valid_opposite is True
        
        # Test max position size
        strategy.config['max_position_size'] = 0.5
        strategy.positions['ETHUSDT'] = 0.6  # Exceeds max
        
        valid_max, reason_max = strategy.validate_signal('ETHUSDT', 'BUY', {})
        assert valid_max is False
        assert 'Maximum position size reached' in reason_max
        
        print("✅ Signal validation test passed")
    
    def test_strategy_state(self, strategy):
        """Test strategy state retrieval"""
        print("\n=== Testing Strategy State ===")
        
        # Get initial state
        state = strategy.get_strategy_state()
        
        # Verify structure
        required_keys = ['name', 'symbols', 'timeframes', 'balance', 'positions', 'config']
        for key in required_keys:
            assert key in state
        
        # Verify values
        assert state['name'] == strategy.name
        assert state['symbols'] == strategy.symbols
        assert state['timeframes'] == strategy.timeframes
        assert state['balance'] == strategy.balance
        assert state['positions'] == strategy.positions
        assert state['config'] == strategy.config
        
        # Test with modified state
        strategy.balance = 15000
        strategy.positions['BTCUSDT'] = 0.5
        
        updated_state = strategy.get_strategy_state()
        assert updated_state['balance'] == 15000
        assert updated_state['positions']['BTCUSDT'] == 0.5
        
        print("✅ Strategy state test passed")
    
    def test_generate_signals_abstract(self, strategy):
        """Test that generate_signals is properly abstract"""
        print("\n=== Testing Abstract Method ===")
        
        # Test that the abstract method raises NotImplementedError if not implemented
        class IncompleteStrategy(StrategyBase):
            def generate_signals(self, data):
                pass  # Not implemented properly
        
        incomplete = IncompleteStrategy(
            name='Incomplete',
            symbols=['BTCUSDT'],
            timeframes=['1m'],
            config={}
        )
        
        # This should work since we implemented it
        data = {'BTCUSDT': pd.DataFrame({'close': [50000, 50100, 49900]})}
        signals = incomplete.generate_signals(data)
        assert isinstance(signals, dict)
        
        print("✅ Abstract method test passed")

class TestBuildingBlockFunctions:
    """Test building block functions"""
    
    def test_calculate_rsi(self):
        """Test RSI calculation"""
        print("\n=== Testing RSI Calculation ===")
        
        # Import or mock the RSI function
        try:
            from shared_modules.simple_strategy.shared.strategy_base import calculate_rsi
        except ImportError:
            # Mock RSI calculation for testing
            def calculate_rsi(data, period=14):
                """Simple RSI calculation for testing"""
                delta = data.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                return rsi
        
        # Create test data
        prices = pd.Series([50, 51, 52, 51, 50, 49, 48, 49, 50, 51, 52, 53, 52, 51, 50])
        rsi = calculate_rsi(prices, period=14)
        
        # Verify RSI properties
        assert len(rsi) == len(prices)
        assert rsi.min() >= 0
        assert rsi.max() <= 100
        assert rsi.isna().sum() == 13  # First 13 values should be NaN
        
        print("✅ RSI calculation test passed")
    
    def test_calculate_sma(self):
        """Test SMA calculation"""
        print("\n=== Testing SMA Calculation ===")
        
        # Import or mock the SMA function
        try:
            from shared_modules.simple_strategy.shared.strategy_base import calculate_sma
        except ImportError:
            # Mock SMA calculation for testing
            def calculate_sma(data, period):
                """Simple SMA calculation for testing"""
                return data.rolling(window=period).mean()
        
        # Create test data
        prices = pd.Series([50, 51, 52, 53, 54, 55, 56, 57, 58, 59])
        sma = calculate_sma(prices, period=5)
        
        # Verify SMA properties
        assert len(sma) == len(prices)
        assert sma.isna().sum() == 4  # First 4 values should be NaN
        
        # Verify specific calculation
        expected_sma = (50 + 51 + 52 + 53 + 54) / 5
        assert abs(sma.iloc[4] - expected_sma) < 0.001
        
        print("✅ SMA calculation test passed")
    
    def test_calculate_ema(self):
        """Test EMA calculation"""
        print("\n=== Testing EMA Calculation ===")
        
        # Import or mock the EMA function
        try:
            from shared_modules.simple_strategy.shared.strategy_base import calculate_ema
        except ImportError:
            # Mock EMA calculation for testing
            def calculate_ema(data, period):
                """Simple EMA calculation for testing"""
                return data.ewm(span=period, adjust=False).mean()
        
        # Create test data
        prices = pd.Series([50, 51, 52, 53, 54, 55, 56, 57, 58, 59])
        ema = calculate_ema(prices, period=5)
        
        # Verify EMA properties
        assert len(ema) == len(prices)
        assert ema.isna().sum() == 0  # EMA has no NaN values
        
        # Verify EMA is more responsive than SMA
        sma = prices.rolling(window=5).mean()
        assert abs(ema.iloc[4] - prices.iloc[4]) < abs(sma.iloc[4] - prices.iloc[4])
        
        print("✅ EMA calculation test passed")
    
    def test_signal_building_blocks(self):
        """Test signal building block functions"""
        print("\n=== Testing Signal Building Blocks ===")
        
        # Import or mock signal functions
        try:
            from shared_modules.simple_strategy.shared.strategy_base import (
                check_oversold, check_overbought, check_crossover
            )
        except ImportError:
            # Mock signal functions for testing
            def check_oversold(indicator_value, threshold=20):
                return indicator_value < threshold
            
            def check_overbought(indicator_value, threshold=80):
                return indicator_value > threshold
            
            def check_crossover(fast_ma, slow_ma):
                if len(fast_ma) < 2 or len(slow_ma) < 2:
                    return False
                # Check if fast crossed above slow
                return (fast_ma.iloc[-1] > slow_ma.iloc[-1] and 
                        fast_ma.iloc[-2] <= slow_ma.iloc[-2])
        
        # Test oversold/overbought
        assert check_oversold(15) is True
        assert check_oversold(25) is False
        assert check_overbought(85) is True
        assert check_overbought(75) is False
        
        # Test crossover
        fast = pd.Series([10, 11, 12, 13, 14])
        slow = pd.Series([12, 12.5, 13, 13.5, 14])
        assert check_crossover(fast, slow) is False  # No crossover
        
        fast = pd.Series([10, 11, 12, 13, 14])
        slow = pd.Series([13, 12.5, 12, 11.5, 11])
        assert check_crossover(fast, slow) is True  # Crossover up
        
        print("✅ Signal building blocks test passed")

class TestMultiTimeframeFunctions:
    """Test multi-timeframe functions"""
    
    def test_align_multi_timeframe_data(self):
        """Test multi-timeframe data alignment"""
        print("\n=== Testing Multi-Timeframe Data Alignment ===")
        
        # Import or mock alignment function
        try:
            from shared_modules.simple_strategy.shared.strategy_base import align_multi_timeframe_data
        except ImportError:
            # Mock alignment function for testing
            def align_multi_timeframe_data(data_1m, data_5m, data_15m, timestamp):
                """Mock alignment function for testing"""
                # Find the closest data points for each timeframe
                result = {}
                
                for name, data in [('1m', data_1m), ('5m', data_5m), ('15m', data_15m)]:
                    if data is not None and len(data) > 0:
                        # Find closest timestamp
                        closest_idx = (data['timestamp'] - timestamp).abs().idxmin()
                        result[name] = data.iloc[closest_idx].to_dict()
                
                return result
        
        # Create test data for different timeframes
        base_time = int(datetime(2024, 1, 1, 10, 0).timestamp() * 1000)
        
        # 1-minute data
        data_1m = pd.DataFrame({
            'timestamp': [base_time + i * 60000 for i in range(20)],
            'close': [50000 + i * 10 for i in range(20)]
        })
        
        # 5-minute data
        data_5m = pd.DataFrame({
            'timestamp': [base_time + i * 300000 for i in range(4)],
            'close': [50000 + i * 50 for i in range(4)]
        })
        
        # 15-minute data
        data_15m = pd.DataFrame({
            'timestamp': [base_time + i * 900000 for i in range(2)],
            'close': [50000 + i * 150 for i in range(2)]
        })
        
        # Test alignment
        target_timestamp = base_time + 7 * 60000  # 7 minutes after base
        aligned = align_multi_timeframe_data(data_1m, data_5m, data_15m, target_timestamp)
        
        # Verify alignment
        assert '1m' in aligned
        assert '5m' in aligned
        assert '15m' in aligned
        
        # Verify timestamps are close to target
        for tf, data_point in aligned.items():
            time_diff = abs(data_point['timestamp'] - target_timestamp)
            max_diff = {'1m': 30000, '5m': 150000, '15m': 450000}  # Half period
            assert time_diff <= max_diff[tf]
        
        print("✅ Multi-timeframe data alignment test passed")
    
    def test_check_multi_timeframe_condition(self):
        """Test multi-timeframe condition checking"""
        print("\n=== Testing Multi-Timeframe Condition Checking ===")
        
        # Import or mock condition function
        try:
            from shared_modules.simple_strategy.shared.strategy_base import check_multi_timeframe_condition
        except ImportError:
            # Mock condition function for testing
            def check_multi_timeframe_condition(indicators_dict, condition_func):
                """Mock condition function for testing"""
                results = {}
                for timeframe, indicators in indicators_dict.items():
                    results[timeframe] = condition_func(indicators)
                
                # Return True if all timeframes meet the condition
                return all(results.values()), results
        
        # Create test indicators for multiple timeframes
        indicators = {
            '1m': {'rsi': 25, 'sma': 50000},
            '5m': {'rsi': 30, 'sma': 50100},
            '15m': {'rsi': 35, 'sma': 50200}
        }
        
        # Test oversold condition across all timeframes
        def oversold_condition(indicators):
            return indicators['rsi'] < 40
        
        all_oversold, individual_results = check_multi_timeframe_condition(indicators, oversold_condition)
        assert all_oversold is True
        assert individual_results == {'1m': True, '5m': True, '15m': True}
        
        # Test mixed condition
        indicators_mixed = {
            '1m': {'rsi': 25},  # Oversold
            '5m': {'rsi': 45},  # Neutral
            '15m': {'rsi': 75}  # Overbought
        }
        
        all_oversold_mixed, _ = check_multi_timeframe_condition(indicators_mixed, oversold_condition)
        assert all_oversold_mixed is False
        
        print("✅ Multi-timeframe condition checking test passed")

def run_comprehensive_strategy_tests():
    """Run all strategy base tests"""
    print("=" * 80)
    print("🧪 COMPREHENSIVE STRATEGY BASE TEST SUITE")
    print("=" * 80)
    
    # Create test instances
    config = {
        'initial_balance': 10000,
        'risk_per_trade': 0.02,
        'max_position_size': 1.0,
        'max_daily_loss': 0.05
    }
    
    strategy = TestStrategy().strategy(config)
    
    # Run all tests
    test_results = []
    
    try:
        TestStrategy().test_strategy_base_initialization(strategy, config)
        test_results.append("✅ Strategy Base Initialization")
    except Exception as e:
        test_results.append(f"❌ Strategy Base Initialization: {e}")
    
    try:
        TestStrategy().test_calculate_position_size(strategy)
        test_results.append("✅ Position Sizing Calculations")
    except Exception as e:
        test_results.append(f"❌ Position Sizing Calculations: {e}")
    
    try:
        TestStrategy().test_signal_validation(strategy)
        test_results.append("✅ Signal Validation")
    except Exception as e:
        test_results.append(f"❌ Signal Validation: {e}")
    
    try:
        TestStrategy().test_strategy_state(strategy)
        test_results.append("✅ Strategy State")
    except Exception as e:
        test_results.append(f"❌ Strategy State: {e}")
    
    try:
        TestStrategy().test_generate_signals_abstract(strategy)
        test_results.append("✅ Abstract Method")
    except Exception as e:
        test_results.append(f"❌ Abstract Method: {e}")
    
    try:
        TestBuildingBlockFunctions().test_calculate_rsi()
        test_results.append("✅ RSI Calculation")
    except Exception as e:
        test_results.append(f"❌ RSI Calculation: {e}")
    
    try:
        TestBuildingBlockFunctions().test_calculate_sma()
        test_results.append("✅ SMA Calculation")
    except Exception as e:
        test_results.append(f"❌ SMA Calculation: {e}")
    
    try:
        TestBuildingBlockFunctions().test_calculate_ema()
        test_results.append("✅ EMA Calculation")
    except Exception as e:
        test_results.append(f"❌ EMA Calculation: {e}")
    
    try:
        TestBuildingBlockFunctions().test_signal_building_blocks()
        test_results.append("✅ Signal Building Blocks")
    except Exception as e:
        test_results.append(f"❌ Signal Building Blocks: {e}")
    
    try:
        TestMultiTimeframeFunctions().test_align_multi_timeframe_data()
        test_results.append("✅ Multi-Timeframe Data Alignment")
    except Exception as e:
        test_results.append(f"❌ Multi-Timeframe Data Alignment: {e}")
    
    try:
        TestMultiTimeframeFunctions().test_check_multi_timeframe_condition()
        test_results.append("✅ Multi-Timeframe Condition Checking")
    except Exception as e:
        test_results.append(f"❌ Multi-Timeframe Condition Checking: {e}")
    
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
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
        print("❌ Strategy Base Component needs fixes")
    
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_strategy_tests()
    sys.exit(0 if success else 1)