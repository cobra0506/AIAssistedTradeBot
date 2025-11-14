"""
Test 03: Performance Calculation for Paper Trading
Tests the performance metrics calculation functionality
"""
import unittest
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

class TestPerformanceCalculation(unittest.TestCase):
    """Test performance calculation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        print("\n" + "="*50)
        print("Setting up Performance Calculation Test")
        print("="*50)
        
        # Create engine (without exchange connection for now)
        from simple_strategy.trading.paper_trading_engine import PaperTradingEngine
        self.engine = PaperTradingEngine("bybit_demo", "Strategy_1_Trend_Following", 1000)
        self.engine.exchange = None  # Skip exchange connection
    
    def test_performance_calculation_method_exists(self):
        """Test that calculate_performance_metrics method exists"""
        print("\n--- Testing Performance Method Exists ---")
        
        # Check if method exists
        self.assertTrue(hasattr(self.engine, 'calculate_performance_metrics'),
                       "calculate_performance_metrics method not found")
        
        print("✅ calculate_performance_metrics method exists")
    
    def test_performance_calculation_with_trades(self):
        """Test performance calculation with some trades"""
        print("\n--- Testing Performance Calculation with Trades ---")
        
        try:
            # Execute some test trades
            self.engine.execute_buy("BTCUSDT", 50000.0)  # Buy at 50k
            self.engine.execute_sell("BTCUSDT", 51000.0)  # Sell at 51k (profit)
            self.engine.execute_buy("BTCUSDT", 52000.0)  # Buy at 52k
            self.engine.execute_sell("BTCUSDT", 51500.0)  # Sell at 51.5k (loss)
            
            # Calculate performance metrics
            metrics = self.engine.calculate_performance_metrics()
            
            if metrics:
                print("✅ Performance calculation successful")
                print(f"   Total trades: {metrics.get('total_trades', 0)}")
                print(f"   Winning trades: {metrics.get('winning_trades', 0)}")
                print(f"   Win rate: {metrics.get('win_rate', 0):.2f}%")
                print(f"   Total return: {metrics.get('total_return', 0):.2f}%")
                print(f"   Current balance: ${metrics.get('current_balance', 0):.2f}")
                
                # Validate metrics structure
                required_keys = ['total_trades', 'winning_trades', 'win_rate', 
                               'total_return', 'current_balance', 'initial_balance']
                for key in required_keys:
                    self.assertIn(key, metrics, f"Missing metric: {key}")
                
                # Validate values make sense
                self.assertEqual(metrics['total_trades'], 4)
                self.assertEqual(metrics['winning_trades'], 1)  # Only first trade was profitable
                self.assertEqual(metrics['win_rate'], 25.0)  # 1/4 = 25%
                self.assertEqual(metrics['initial_balance'], 1000.0)
                
            else:
                print("❌ Performance calculation returned None")
                self.fail("Performance calculation returned None")
                
        except Exception as e:
            print(f"❌ Performance calculation error: {e}")
            self.fail(f"Performance calculation failed: {e}")
    
    def test_performance_calculation_no_trades(self):
        """Test performance calculation with no trades"""
        print("\n--- Testing Performance Calculation with No Trades ---")
        
        try:
            # Clear any existing trades
            self.engine.trades = []
            
            # Calculate performance metrics
            metrics = self.engine.calculate_performance_metrics()
            
            if metrics:
                print("✅ Performance calculation with no trades successful")
                print(f"   Total trades: {metrics.get('total_trades', 0)}")
                print(f"   Win rate: {metrics.get('win_rate', 0):.2f}%")
                print(f"   Total return: {metrics.get('total_return', 0):.2f}%")
                
                # Validate metrics for no trades scenario
                self.assertEqual(metrics['total_trades'], 0)
                self.assertEqual(metrics['winning_trades'], 0)
                self.assertEqual(metrics['win_rate'], 0.0)
                self.assertEqual(metrics['total_return'], 0.0)
                self.assertEqual(metrics['current_balance'], metrics['initial_balance'])
                
            else:
                print("❌ Performance calculation returned None")
                self.fail("Performance calculation returned None")
                
        except Exception as e:
            print(f"❌ Performance calculation error: {e}")
            self.fail(f"Performance calculation failed: {e}")

if __name__ == '__main__':
    print("Testing Paper Trading - Performance Calculation")
    print("=" * 50)
    unittest.main(verbosity=2)