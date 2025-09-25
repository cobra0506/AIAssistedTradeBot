# debug_failing_tests.py - FIXED VERSION
import sys
import os
import pandas as pd
import numpy as np

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions we need to test
from simple_strategy.shared.strategy_base import (
    StrategyBase,
    calculate_rsi_func,
    calculate_srsi_func,  # Import with _func suffix
    calculate_stochastic_func
)

# Create a simple test strategy class
class TestStrategy(StrategyBase):
    def generate_signals(self, data):
        return {}

# Test 1: Strategy State
def test_strategy_state():
    print("\n=== Testing Strategy State ===")
    try:
        # Create strategy
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
        
        # Get initial state
        state = strategy.get_strategy_state()
        print(f"Initial state: {state}")
        
        # Verify structure
        required_keys = ['name', 'balance', 'initial_balance', 'total_return',
                        'open_positions', 'total_trades', 'symbols', 'timeframes', 'config']
        for key in required_keys:
            if key not in state:
                print(f"❌ Missing key: {key}")
                return False
        
        # Verify values
        if state['name'] != strategy.name:
            print(f"❌ Name mismatch: {state['name']} != {strategy.name}")
            return False
            
        if state['balance'] != strategy.balance:
            print(f"❌ Balance mismatch: {state['balance']} != {strategy.balance}")
            return False
            
        if state['initial_balance'] != strategy.initial_balance:
            print(f"❌ Initial balance mismatch: {state['initial_balance']} != {strategy.initial_balance}")
            return False
            
        if state['total_return'] != 0.0:
            print(f"❌ Total return mismatch: {state['total_return']} != 0.0")
            return False
            
        if state['open_positions'] != 0:
            print(f"❌ Open positions mismatch: {state['open_positions']} != 0")
            return False
            
        if state['total_trades'] != 0:
            print(f"❌ Total trades mismatch: {state['total_trades']} != 0")
            return False
            
        # Test with modified state
        strategy.balance = 15000
        strategy.positions = {'BTCUSDT': {}}
        strategy.trades = [{}]
        updated_state = strategy.get_strategy_state()
        print(f"Updated state: {updated_state}")
        
        if updated_state['balance'] != 15000:
            print(f"❌ Updated balance mismatch: {updated_state['balance']} != 15000")
            return False
            
        # Check total return with tolerance for floating point precision
        expected_return = 0.5  # 50% return
        actual_return = updated_state['total_return']
        if abs(actual_return - expected_return) >= 0.001:
            print(f"❌ Total return mismatch: {actual_return} != {expected_return}")
            return False
            
        if updated_state['open_positions'] != 1:
            print(f"❌ Updated open positions mismatch: {updated_state['open_positions']} != 1")
            return False
            
        if updated_state['total_trades'] != 1:
            print(f"❌ Updated total trades mismatch: {updated_state['total_trades']} != 1")
            return False
        
        print("✅ Strategy state test passed")
        return True
    except Exception as e:
        print(f"❌ Strategy state test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

# Test 2: SRSI Calculation
def test_calculate_srsi():
    """Test SRSI calculation"""
    print("\n=== Testing SRSI Calculation ===")
    try:
        # Use more varied test data to get better SRSI values
        prices = pd.Series([100, 105, 95, 110, 90, 115, 85, 120, 80, 125, 75, 130, 70, 135, 65, 
                           140, 60, 145, 55, 150, 50, 155, 45, 160, 40, 165, 35, 170, 30, 175])
        
        # Calculate SRSI - FIXED: Use the correct function name
        srsi = calculate_srsi_func(prices, period=5)
        
        # Verify basic properties
        assert len(srsi) == len(prices)
        
        # Check that non-NaN values are within expected range
        valid_srsi = srsi.dropna()
        assert len(valid_srsi) > 0  # Should have some valid values
        assert valid_srsi.min() >= 0  # SRSI should be between 0 and 100
        assert valid_srsi.max() <= 100
        
        # Test with different period
        srsi_long = calculate_srsi_func(prices, period=10)
        assert len(srsi_long) == len(prices)
        
        print("✅ SRSI Calculation test passed")
        return True
    except Exception as e:
        print(f"❌ SRSI Calculation test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 DEBUGGING FAILING TESTS")
    print("=" * 80)
    
    test1_result = test_strategy_state()
    test2_result = test_calculate_srsi()  # FIXED: Removed self parameter
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    if test1_result:
        print("✅ Strategy State: PASSED")
    else:
        print("❌ Strategy State: FAILED")
    
    if test2_result:
        print("✅ SRSI Calculation: PASSED")
    else:
        print("❌ SRSI Calculation: FAILED")