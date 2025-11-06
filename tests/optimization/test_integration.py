import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import unittest
from simple_strategy.optimization import BayesianOptimizer, ParameterSpace
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.shared.data_feeder import DataFeeder

class TestOptimizationIntegration(unittest.TestCase):
    
    def setUp(self):
        self.data_feeder = DataFeeder(data_dir='data')
        
    def test_simple_rsi_optimization(self):
        """Test a simple RSI parameter optimization"""
        
        # Create parameter space for RSI
        param_space = ParameterSpace()
        param_space.add_int('rsi_period', 10, 20, step=2)  # Small range for testing
        param_space.add_float('rsi_oversold', 25, 35)
        param_space.add_float('rsi_overbought', 65, 75)
        
        # Create optimizer with very few trials for testing
        optimizer = BayesianOptimizer(
            data_feeder=self.data_feeder,
            study_name='test_rsi_optimization',
            direction='maximize',
            n_trials=3,  # Very few for quick testing
            timeout=60
        )
        
        # Use dates that match your actual data
        best_params, best_score = optimizer.optimize(
            strategy_builder_class=StrategyBuilder,
            parameter_space=param_space,
            symbols=['BTCUSDT'],
            timeframes=['60'],  # Matches your BTCUSDT_60.csv file
            start_date='2025-09-23',  # Start after your data begins
            end_date='2025-10-21',    # End before your data ends
            metric='sharpe_ratio'
        )
        
        # Check that we got some results
        self.assertIsInstance(best_params, dict)
        self.assertIsInstance(best_score, (int, float))
        
        print(f"Test optimization completed. Best score: {best_score}")
        print(f"Best params: {best_params}")

if __name__ == '__main__':
    unittest.main()