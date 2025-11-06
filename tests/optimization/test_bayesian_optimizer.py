import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent  # Goes up 3 levels: tests/optimization/ -> tests/ -> simple_strategy/ -> project_root
sys.path.insert(0, str(project_root))

import unittest
from simple_strategy.optimization import BayesianOptimizer, ParameterSpace
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.shared.data_feeder import DataFeeder
import pandas as pd

class TestBayesianOptimizer(unittest.TestCase):
    
    def setUp(self):
        self.data_feeder = DataFeeder(data_dir='data')
        self.optimizer = BayesianOptimizer(
            data_feeder=self.data_feeder,
            n_trials=5,  # Very few for testing
            timeout=60
        )
    
    def test_parameter_space_creation(self):
        param_space = ParameterSpace()
        param_space.add_int('test_int', 1, 10)
        param_space.add_float('test_float', 0.1, 1.0)
        param_space.add_categorical('test_cat', ['a', 'b', 'c'])
        
        params = param_space.get_parameters()
        self.assertEqual(len(params), 3)
        self.assertEqual(params['test_int']['type'], 'int')
    
    def test_parameter_validation(self):
        param_space = ParameterSpace()
        param_space.add_int('test_int', 1, 10)
        
        self.assertTrue(param_space.validate_params({'test_int': 5}))
        self.assertFalse(param_space.validate_params({'test_int': 15}))
    
    def test_optimizer_initialization(self):
        self.assertIsNotNone(self.optimizer)
        self.assertEqual(self.optimizer.n_trials, 5)
    
    def test_study_creation(self):
        param_space = ParameterSpace()
        param_space.add_int('test_param', 1, 10)
        
        # This should not raise an exception
        try:
            optimizer = BayesianOptimizer(self.data_feeder, n_trials=2)
            # Note: We can't actually run optimization without proper data
            # But we can test the setup
            self.assertIsNotNone(optimizer)
        except Exception as e:
            self.fail(f"Optimizer initialization failed: {e}")

if __name__ == '__main__':
    unittest.main()