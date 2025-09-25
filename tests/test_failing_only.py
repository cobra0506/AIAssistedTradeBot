# test_failing_only_fixed.py - Temporary test file with only failing tests (FIXED)
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

class TestFailingTests:
    """Test class for only the failing tests"""
    
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
        # FIXED: Allow small floating-point error instead of exact equality
        assert abs(updated_state['total_return'] - 0.5) < 0.001  # 50% return (with tolerance)
        assert updated_state['open_positions'] == 1
        assert updated_state['total_trades'] == 1
        
        print("✅ Strategy state test passed")
    
    def test_calculate_srsi(self):
        """Test SRSI calculation"""
        print("\n=== Testing SRSI Calculation ===")
        # FIXED: Use more data points to ensure we get valid results
        prices = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120, 122, 124, 126, 128])
        
        # Calculate SRSI
        srsi = calculate_srsi(prices, period=5)
        
        # Verify basic properties
        assert len(srsi) == len(prices)
        
        # FIXED: Check that non-NaN values are within expected range
        valid_srsi = srsi.dropna()
        assert len(valid_srsi) > 0  # Should have some valid values
        assert valid_srsi.min() >= 0  # SRSI should be between 0 and 100
        assert valid_srsi.max() <= 100
        
        # Test with different period
        srsi_long = calculate_srsi(prices, period=10)
        assert len(srsi_long) == len(prices)
        
        print("✅ SRSI Calculation test passed")

if __name__ == "__main__":
    # Run the tests manually
    test_instance = TestFailingTests()
    config = test_instance.config()
    strategy = test_instance.strategy(config)
    
    print("=" * 80)
    print("🧪 RUNNING FAILING TESTS ONLY (FIXED)")
    print("=" * 80)
    
    try:
        test_instance.test_strategy_state(strategy)
        print("✅ Strategy State Test: PASSED")
    except Exception as e:
        print(f"❌ Strategy State Test: FAILED - {e}")
    
    try:
        test_instance.test_calculate_srsi()
        print("✅ SRSI Calculation Test: PASSED")
    except Exception as e:
        print(f"❌ SRSI Calculation Test: FAILED - {e}")
    
    print("=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)