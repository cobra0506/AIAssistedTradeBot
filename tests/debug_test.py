"""
Debug test to isolate initialization issues
"""
import unittest
import tempfile
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.performance_tracker import PerformanceTracker
from simple_strategy.backtester.position_manager import PositionManager
from simple_strategy.shared.data_feeder import DataFeeder
from simple_strategy.shared.strategy_base import StrategyBase

class DebugInitializationTest(unittest.TestCase):
    """Debug test to check component initialization"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_data_feeder_initialization(self):
        """Test if DataFeeder can be initialized"""
        print("Testing DataFeeder initialization...")
        try:
            data_feeder = DataFeeder(data_dir=self.temp_dir)
            print("✅ DataFeeder initialized successfully")
            self.assertIsNotNone(data_feeder)
        except Exception as e:
            print(f"❌ DataFeeder initialization failed: {e}")
            raise
    
    def test_performance_tracker_initialization(self):
        """Test if PerformanceTracker can be initialized"""
        print("Testing PerformanceTracker initialization...")
        try:
            tracker = PerformanceTracker(initial_balance=10000.0)
            print("✅ PerformanceTracker initialized successfully")
            self.assertIsNotNone(tracker)
        except Exception as e:
            print(f"❌ PerformanceTracker initialization failed: {e}")
            raise
    
    def test_position_manager_initialization(self):
        """Test if PositionManager can be initialized"""
        print("Testing PositionManager initialization...")
        try:
            manager = PositionManager(initial_balance=10000.0)
            print("✅ PositionManager initialized successfully")
            self.assertIsNotNone(manager)
        except Exception as e:
            print(f"❌ PositionManager initialization failed: {e}")
            raise
    
    def test_multisymbol_strategy_import(self):
        """Test if MultiSymbolStrategy can be imported and instantiated"""
        print("Testing MultiSymbolStrategy import...")
        try:
            # First, let's check if we can import it
            from tests.test_complete_backtesting_system import MultiSymbolStrategy
            print("✅ MultiSymbolStrategy imported successfully")
            
            # Now try to instantiate it
            strategy = MultiSymbolStrategy(
                name="DebugStrategy",
                symbols=["BTCUSDT"],
                timeframes=["1m"],
                config={"initial_balance": 10000.0}
            )
            print("✅ MultiSymbolStrategy instantiated successfully")
            self.assertIsNotNone(strategy)
            
        except Exception as e:
            print(f"❌ MultiSymbolStrategy test failed: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise
    
    def test_backtester_with_mock_strategy(self):
        """Test backtester initialization with a simple mock strategy"""
        print("Testing backtester with mock strategy...")
        
        try:
            # Create a simple mock strategy
            class MockStrategy(StrategyBase):
                def generate_signals(self, data):
                    return {"BTCUSDT": {"1m": "HOLD"}}
            
            # Initialize components
            data_feeder = DataFeeder(data_dir=self.temp_dir)
            strategy = MockStrategy(
                name="MockStrategy",
                symbols=["BTCUSDT"],
                timeframes=["1m"],
                config={"initial_balance": 10000.0}
            )
            
            # Try to initialize backtester
            backtester = BacktesterEngine(
                data_feeder=data_feeder,
                strategy=strategy,
                config={"processing_mode": "sequential"}
            )
            
            print("✅ Backtester with mock strategy initialized successfully")
            self.assertIsNotNone(backtester)
            
        except Exception as e:
            print(f"❌ Backtester with mock strategy failed: {e}")
            import traceback
            print(f"❌ Traceback: {traceback.format_exc()}")
            raise

if __name__ == '__main__':
    unittest.main(verbosity=2)