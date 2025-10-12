import os
import importlib.util
from typing import Dict, List, Type
import sys
import glob

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .strategy_builder import StrategyBuilder

class StrategyRegistry:
    def __init__(self):
        self.strategies = {}
        self._discover_strategies()
    
    def _discover_strategies(self):
        # Scan for strategy files in the strategies folder
        strategy_dir = os.path.dirname(__file__)
        
        # Look for files that start with "Strategy_" and end with ".py"
        pattern = os.path.join(strategy_dir, "Strategy_*.py")
        strategy_files = glob.glob(pattern)
        
        for file_path in strategy_files:
            file_name = os.path.basename(file_path)
            strategy_name = file_name.replace('.py', '')
            
            try:
                # Import the strategy file
                spec = importlib.util.spec_from_file_location(strategy_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if it has a create_strategy function
                if hasattr(module, 'create_strategy'):
                    # Get strategy parameters if available
                    params = getattr(module, 'STRATEGY_PARAMETERS', {})
                    
                    self.strategies[strategy_name] = {
                        'module': module,
                        'create_func': getattr(module, 'create_strategy'),
                        'description': getattr(module, '__doc__', 'No description'),
                        'parameters': params
                    }
                    
                    print(f"✅ Loaded strategy: {strategy_name}")
                else:
                    print(f"⚠️ Strategy {strategy_name} missing create_strategy function")
                    
            except Exception as e:
                print(f"❌ Error loading strategy {strategy_name}: {e}")
    
    def get_all_strategies(self) -> Dict[str, dict]:
        return self.strategies
    
    def get_strategy(self, name: str):
        return self.strategies.get(name)
    
    def create_strategy_instance(self, name: str, **kwargs):
        if name in self.strategies:
            return self.strategies[name]['create_func'](**kwargs)
        return None