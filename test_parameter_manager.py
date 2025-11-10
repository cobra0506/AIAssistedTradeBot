import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simple_strategy.trading.parameter_manager import ParameterManager

def main():
    print("Testing ParameterManager...")
    
    # Create the manager
    pm = ParameterManager()
    
    # Test adding parameters
    test_params = {
        'rsi_period': 14,
        'rsi_oversold': 30,
        'rsi_overbought': 70
    }
    pm.update_parameters('Test_Strategy', test_params)
    
    # Test retrieving parameters
    retrieved = pm.get_parameters('Test_Strategy')
    print("Retrieved parameters:", retrieved)
    
    # Test getting all strategies
    strategies = pm.get_all_strategies()
    print("All strategies:", strategies)
    
    print("Test completed successfully!")

if __name__ == "__main__":
    main()
    