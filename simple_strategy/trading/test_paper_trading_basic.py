import unittest
import os
import sys
import time
import threading

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from simple_strategy.trading.paper_trading_engine import PaperTradingEngine

class TestPaperTradingBasic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = PaperTradingEngine("Demo Account 1", "Strategy_Mean_Reversion", 1000)
    
    def test_initialization(self):
        """Test that the engine initializes correctly"""
        self.assertEqual(self.engine.api_account, "Demo Account 1")
        self.assertEqual(self.engine.strategy_name, "Strategy_Mean_Reversion")
        self.assertEqual(self.engine.simulated_balance, 1000.0)
        self.assertEqual(self.engine.initial_balance, 1000.0)
        self.assertFalse(self.engine.is_running)
        self.assertEqual(len(self.engine.trades), 0)
        self.assertEqual(len(self.engine.current_positions), 0)
    
    def test_exchange_connection(self):
        """Test that Bybit connection works"""
        result = self.engine.initialize_exchange()
        self.assertTrue(result)
        self.assertIsNotNone(self.engine.exchange)
        self.assertIsNotNone(self.engine.bybit_balance)
    
    def test_strategy_loading(self):
        """Test that strategy loading works"""
        result = self.engine.load_strategy()
        self.assertTrue(result)
        self.assertIsNotNone(self.engine.strategy)
    
    def test_trade_execution(self):
        """Test that trade execution works"""
        # Test buy
        self.engine.execute_buy("BTCUSDT", 50000.0)
        self.assertEqual(len(self.engine.trades), 1)
        self.assertEqual(self.engine.trades[0]['type'], 'BUY')
        self.assertEqual(self.engine.trades[0]['symbol'], 'BTCUSDT')
        
        # Test sell
        self.engine.execute_sell("BTCUSDT", 51000.0)
        self.assertEqual(len(self.engine.trades), 2)
        self.assertEqual(self.engine.trades[1]['type'], 'SELL')
        self.assertEqual(self.engine.trades[1]['symbol'], 'BTCUSDT')
    
    def test_position_tracking(self):
        """Test that position tracking works"""
        # Execute a buy
        self.engine.execute_buy("BTCUSDT", 50000.0)
        
        # Check position was created
        self.assertIn("BTCUSDT", self.engine.current_positions)
        self.assertGreater(self.engine.current_positions["BTCUSDT"], 0)
        
        # Execute a sell
        self.engine.execute_sell("BTCUSDT", 51000.0)
        
        # Check position was closed
        self.assertEqual(self.engine.current_positions["BTCUSDT"], 0)

if __name__ == '__main__':
    unittest.main()