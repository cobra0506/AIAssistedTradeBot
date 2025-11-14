"""
Test 02: Trade Execution for Paper Trading
Tests the trade execution functionality (buy/sell operations)
"""
import unittest
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

class TestTradeExecution(unittest.TestCase):
    """Test trade execution functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        print("\n" + "="*50)
        print("Setting up Trade Execution Test")
        print("="*50)
        
        # Create engine (without exchange connection for now)
        from simple_strategy.trading.paper_trading_engine import PaperTradingEngine
        self.engine = PaperTradingEngine("bybit_demo", "Strategy_1_Trend_Following", 1000)
        
        # Skip exchange connection for this test
        self.engine.exchange = None  # We'll test trade logic without real API
    
    def test_buy_execution(self):
        """Test buy trade execution"""
        print("\n--- Testing Buy Execution ---")
        
        try:
            initial_balance = self.engine.simulated_balance
            
            # Execute buy trade
            trade = self.engine.execute_buy("BTCUSDT", 50000.0)
            
            if trade:
                # Check trade was recorded
                self.assertEqual(len(self.engine.trades), 1)
                self.assertEqual(trade['type'], 'BUY')
                self.assertEqual(trade['symbol'], 'BTCUSDT')
                self.assertEqual(trade['price'], 50000.0)
                
                # Check balance was updated
                self.assertLess(self.engine.simulated_balance, initial_balance)
                
                print("✅ Buy execution successful")
                print(f"   Trade: {trade}")
                print(f"   Balance before: ${initial_balance}")
                print(f"   Balance after: ${self.engine.simulated_balance}")
            else:
                print("❌ Buy execution failed - no trade returned")
                self.fail("Buy execution failed - no trade returned")
                
        except Exception as e:
            print(f"❌ Buy execution error: {e}")
            self.fail(f"Buy execution failed: {e}")
    
    def test_sell_execution(self):
        """Test sell trade execution"""
        print("\n--- Testing Sell Execution ---")
        
        try:
            # First execute a buy to have something to sell
            self.engine.execute_buy("BTCUSDT", 50000.0)
            initial_balance = self.engine.simulated_balance
            
            # Execute sell trade
            trade = self.engine.execute_sell("BTCUSDT", 51000.0)
            
            if trade:
                # Check trade was recorded
                self.assertEqual(len(self.engine.trades), 2)
                self.assertEqual(trade['type'], 'SELL')
                self.assertEqual(trade['symbol'], 'BTCUSDT')
                self.assertEqual(trade['price'], 51000.0)
                
                # Check balance was updated
                self.assertGreater(self.engine.simulated_balance, initial_balance)
                
                print("✅ Sell execution successful")
                print(f"   Trade: {trade}")
                print(f"   Balance before: ${initial_balance}")
                print(f"   Balance after: ${self.engine.simulated_balance}")
            else:
                print("❌ Sell execution failed - no trade returned")
                self.fail("Sell execution failed - no trade returned")
                
        except Exception as e:
            print(f"❌ Sell execution error: {e}")
            self.fail(f"Sell execution failed: {e}")
    
    def test_position_tracking(self):
        """Test position tracking after trades"""
        print("\n--- Testing Position Tracking ---")
        
        try:
            # Clear any existing positions
            self.engine.current_positions = {}
            
            # Execute buy to create position
            self.engine.execute_buy("BTCUSDT", 50000.0)
            
            # Check position was created
            if "BTCUSDT" in self.engine.current_positions:
                position = self.engine.current_positions["BTCUSDT"]
                print(f"✅ Position created after buy: {position}")
                
                # Check if position is a dict with quantity (current implementation)
                self.assertIsInstance(position, dict, 
                    f"Position should be a dict, got {type(position)}")
                self.assertIn('quantity', position, "Position dict should have 'quantity' key")
                self.assertGreater(position['quantity'], 0, "Position quantity should be greater than 0")
            else:
                print("❌ Position not created after buy")
                self.fail("Position not created after buy")
            
            # Execute sell to close position
            self.engine.execute_sell("BTCUSDT", 51000.0)
            
            # Check position was closed
            if self.engine.current_positions["BTCUSDT"]["quantity"] == 0:
                print("✅ Position closed after sell")
            else:
                print(f"❌ Position not closed: {self.engine.current_positions['BTCUSDT']}")
                self.fail("Position not closed after sell")
                
        except Exception as e:
            print(f"❌ Position tracking error: {e}")
            self.fail(f"Position tracking failed: {e}")

if __name__ == '__main__':
    print("Testing Paper Trading - Trade Execution")
    print("=" * 50)
    unittest.main(verbosity=2)