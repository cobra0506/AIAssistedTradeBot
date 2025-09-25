"""
Unit tests for Position Manager
Thorough testing to ensure 100% functionality
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path

# Add the project root to the Python path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.backtester.position_manager import PositionManager, Position, Trade

class TestPositionManager(unittest.TestCase):
    """Comprehensive test suite for PositionManager"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.position_manager = PositionManager(
            initial_balance=10000.0,
            max_positions=3,
            max_risk_per_trade=0.02  # 2% risk per trade = $200
        )
        
    def test_initialization(self):
        """Test PositionManager initialization"""
        # Verify initial state
        self.assertEqual(self.position_manager.initial_balance, 10000.0)
        self.assertEqual(self.position_manager.current_balance, 10000.0)
        self.assertEqual(self.position_manager.max_positions, 3)
        self.assertEqual(self.position_manager.max_risk_per_trade, 0.02)
        self.assertEqual(len(self.position_manager.positions), 0)
        self.assertEqual(len(self.position_manager.completed_trades), 0)
        
    def test_can_open_position_valid(self):
        """Test checking if position can be opened - valid case"""
        # Test valid position with realistic size
        can_open, reason = self.position_manager.can_open_position(
            symbol='BTCUSDT',
            position_size=0.01,  # 0.01 * 20000 = $200, which is exactly 2% risk
            entry_price=20000.0
        )
        
        # Verify can open position
        self.assertTrue(can_open)
        self.assertEqual(reason, "Can open position")
        
    def test_can_open_position_already_open(self):
        """Test checking if position can be opened - position already open"""
        # First open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Try to open another position for same symbol
        can_open, reason = self.position_manager.can_open_position(
            symbol='BTCUSDT',
            position_size=0.01,  # Realistic size
            entry_price=20000.0
        )
        
        # Verify cannot open position
        self.assertFalse(can_open)
        self.assertIn("Position already open", reason)
        
    def test_can_open_position_max_positions_reached(self):
        """Test checking if position can be opened - max positions reached"""
        # Create a new position manager with higher risk limit for this test
        test_manager = PositionManager(
            initial_balance=10000.0,
            max_positions=2,  # Lower max positions for easier testing
            max_risk_per_trade=0.05  # 5% risk per trade = $500
        )
        
        # Open maximum number of positions
        symbols = ['BTCUSDT', 'ETHUSDT']
        for symbol in symbols:
            test_manager.open_position(
                symbol=symbol,
                direction='long',
                size=0.01,  # Realistic size
                entry_price=20000.0,
                timestamp=datetime(2023, 1, 1, 10, 0)
            )
        
        # Try to open another position
        can_open, reason = test_manager.can_open_position(
            symbol='SOLUSDT',
            position_size=0.01,  # Realistic size
            entry_price=20000.0
        )
        
        # Verify cannot open position
        self.assertFalse(can_open)
        self.assertIn("Maximum positions", reason)
        
    def test_can_open_position_insufficient_balance(self):
        """Test checking if position can be opened - insufficient balance"""
        # Try to open position larger than balance
        can_open, reason = self.position_manager.can_open_position(
            symbol='BTCUSDT',
            position_size=1.0,  # 1.0 * 20000 = $20000, which exceeds $10000 balance
            entry_price=20000.0
        )
        
        # Verify cannot open position
        self.assertFalse(can_open)
        self.assertIn("Insufficient balance", reason)
        
    def test_can_open_position_risk_limit_exceeded(self):
        """Test checking if position can be opened - risk limit exceeded"""
        # Try to open position that exceeds risk limit
        can_open, reason = self.position_manager.can_open_position(
            symbol='BTCUSDT',
            position_size=0.011,  # 0.011 * 20000 = $220, which exceeds 2% risk ($200)
            entry_price=20000.0
        )
        
        # Verify cannot open position
        self.assertFalse(can_open)
        self.assertIn("exceeds risk limit", reason)
        
    def test_open_position_valid(self):
        """Test opening a valid position"""
        # Open position with realistic size
        result = self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Verify success
        self.assertTrue(result)
        
        # Verify position was created
        self.assertEqual(len(self.position_manager.positions), 1)
        self.assertIn('BTCUSDT', self.position_manager.positions)
        
        # Verify position details
        position = self.position_manager.positions['BTCUSDT']
        self.assertEqual(position.symbol, 'BTCUSDT')
        self.assertEqual(position.direction, 'long')
        self.assertEqual(position.size, 0.01)
        self.assertEqual(position.entry_price, 20000.0)
        self.assertEqual(position.current_price, 20000.0)
        
        # Verify balance was reduced
        self.assertEqual(self.position_manager.current_balance, 9800.0)  # 10000 - 200
        
    def test_open_position_invalid_direction(self):
        """Test opening position with invalid direction"""
        # Try to open position with invalid direction
        result = self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='invalid',  # Invalid direction
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Verify failure
        self.assertFalse(result)
        self.assertEqual(len(self.position_manager.positions), 0)
        self.assertEqual(self.position_manager.current_balance, 10000.0)  # Balance unchanged
        
    def test_open_position_cannot_open(self):
        """Test opening position when cannot open"""
        # First open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Try to open another position for same symbol
        result = self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 11, 0)
        )
        
        # Verify failure
        self.assertFalse(result)
        self.assertEqual(len(self.position_manager.positions), 1)  # Still only one position
        
    def test_close_position_valid(self):
        """Test closing a valid position"""
        # First open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Close position
        trade = self.position_manager.close_position(
            symbol='BTCUSDT',
            exit_price=21000.0,
            timestamp=datetime(2023, 1, 1, 11, 0)
        )
        
        # Verify trade was created
        self.assertIsNotNone(trade)
        self.assertIsInstance(trade, Trade)
        self.assertEqual(trade.symbol, 'BTCUSDT')
        self.assertEqual(trade.direction, 'long')
        self.assertEqual(trade.entry_price, 20000.0)
        self.assertEqual(trade.exit_price, 21000.0)
        self.assertEqual(trade.pnl, 10.0)  # (21000 - 20000) * 0.01
        
        # Verify position was removed
        self.assertEqual(len(self.position_manager.positions), 0)
        
        # Verify balance was updated correctly
        # Initial: $10,000
        # After opening: $10,000 - $200 = $9,800
        # After closing: $9,800 + $200 (margin returned) + $10 (profit) = $10,010
        self.assertEqual(self.position_manager.current_balance, 10010.0)
        
        # Verify trade was added to completed trades
        self.assertEqual(len(self.position_manager.completed_trades), 1)
        
    def test_close_position_no_position(self):
        """Test closing position when no position exists"""
        # Try to close non-existent position
        trade = self.position_manager.close_position(
            symbol='BTCUSDT',
            exit_price=21000.0,
            timestamp=datetime(2023, 1, 1, 11, 0)
        )
        
        # Verify no trade was created
        self.assertIsNone(trade)
        self.assertEqual(len(self.position_manager.positions), 0)
        self.assertEqual(len(self.position_manager.completed_trades), 0)
        
    def test_update_position_value(self):
        """Test updating position value"""
        # Open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Update position value
        self.position_manager.update_position_value(
            symbol='BTCUSDT',
            current_price=21000.0
        )
        
        # Verify position was updated
        position = self.position_manager.positions['BTCUSDT']
        self.assertEqual(position.current_price, 21000.0)
        # Fix: The actual unrealized P&L is $10.00, not $100.00
        self.assertEqual(position.unrealized_pnl, 10.0)  # (21000 - 20000) * 0.01
        
    def test_update_position_value_no_position(self):
        """Test updating position value when no position exists"""
        # Try to update non-existent position
        self.position_manager.update_position_value(
            symbol='BTCUSDT',
            current_price=21000.0
        )
        
        # Verify no error occurred (should silently fail)
        self.assertEqual(len(self.position_manager.positions), 0)
        
    def test_get_position(self):
        """Test getting position details"""
        # Open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Get position
        position = self.position_manager.get_position('BTCUSDT')
        
        # Verify position details
        self.assertIsNotNone(position)
        self.assertEqual(position.symbol, 'BTCUSDT')
        self.assertEqual(position.direction, 'long')
        self.assertEqual(position.size, 0.01)
        
    def test_get_position_no_position(self):
        """Test getting position when no position exists"""
        # Get non-existent position
        position = self.position_manager.get_position('BTCUSDT')
        
        # Verify no position returned
        self.assertIsNone(position)
        
    def test_get_all_positions(self):
        """Test getting all positions"""
        # Create a new position manager with higher risk limit for this test
        test_manager = PositionManager(
            initial_balance=10000.0,
            max_positions=3,
            max_risk_per_trade=0.05  # 5% risk per trade = $500
        )
        
        # Open multiple positions with realistic sizes
        symbols = ['BTCUSDT', 'ETHUSDT']
        for symbol in symbols:
            test_manager.open_position(
                symbol=symbol,
                direction='long',
                size=0.01,  # Realistic size
                entry_price=20000.0,
                timestamp=datetime(2023, 1, 1, 10, 0)
            )
        
        # Get all positions
        all_positions = test_manager.get_all_positions()
        
        # Verify all positions returned
        self.assertEqual(len(all_positions), 2)
        self.assertIn('BTCUSDT', all_positions)
        self.assertIn('ETHUSDT', all_positions)
        
    def test_get_all_positions_empty(self):
        """Test getting all positions when no positions exist"""
        # Get all positions
        all_positions = self.position_manager.get_all_positions()
        
        # Verify no positions returned
        self.assertEqual(len(all_positions), 0)
        
    def test_get_account_summary(self):
        """Test getting account summary"""
        # Open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Get account summary
        summary = self.position_manager.get_account_summary()
        
        # Verify summary structure
        self.assertIsInstance(summary, dict)
        self.assertIn('initial_balance', summary)
        self.assertIn('current_balance', summary)
        self.assertIn('total_margin_used', summary)
        self.assertIn('total_unrealized_pnl', summary)
        self.assertIn('total_realized_pnl', summary)
        self.assertIn('total_portfolio_value', summary)
        self.assertIn('open_positions_count', summary)
        self.assertIn('completed_trades_count', summary)
        
        # Verify values
        self.assertEqual(summary['initial_balance'], 10000.0)
        self.assertEqual(summary['current_balance'], 9800.0)
        self.assertEqual(summary['total_margin_used'], 200.0)
        self.assertEqual(summary['open_positions_count'], 1)
        self.assertEqual(summary['completed_trades_count'], 0)
        
    def test_get_account_summary_empty(self):
        """Test getting account summary when no positions exist"""
        # Get account summary
        summary = self.position_manager.get_account_summary()
        
        # Verify values
        self.assertEqual(summary['initial_balance'], 10000.0)
        self.assertEqual(summary['current_balance'], 10000.0)
        self.assertEqual(summary['total_margin_used'], 0.0)
        self.assertEqual(summary['open_positions_count'], 0)
        self.assertEqual(summary['completed_trades_count'], 0)
        
    def test_get_trade_history(self):
        """Test getting trade history"""
        # Open and close a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        self.position_manager.close_position(
            symbol='BTCUSDT',
            exit_price=21000.0,
            timestamp=datetime(2023, 1, 1, 11, 0)
        )
        
        # Get trade history
        trade_history = self.position_manager.get_trade_history()
        
        # Verify trade history
        self.assertEqual(len(trade_history), 1)
        self.assertEqual(trade_history[0].symbol, 'BTCUSDT')
        # Fix: The actual P&L is $10.00, not $100.00
        self.assertEqual(trade_history[0].pnl, 10.0)
        
    def test_get_trade_history_empty(self):
        """Test getting trade history when no trades exist"""
        # Get trade history
        trade_history = self.position_manager.get_trade_history()
        
        # Verify no trades
        self.assertEqual(len(trade_history), 0)
        
    def test_calculate_position_size(self):
        """Test calculating position size"""
        # Calculate position size
        position_size = self.position_manager.calculate_position_size(
            symbol='BTCUSDT',
            price=20000.0
        )
        
        # Verify calculation
        expected_size = (10000.0 * 0.02) / 20000.0  # balance * risk_per_trade / price
        self.assertAlmostEqual(position_size, expected_size, places=5)
        
    def test_calculate_position_size_custom_risk(self):
        """Test calculating position size with custom risk"""
        # Calculate position size with custom risk
        position_size = self.position_manager.calculate_position_size(
            symbol='BTCUSDT',
            price=20000.0,
            risk_fraction=0.05  # 5% risk
        )
        
        # Verify calculation
        expected_size = (10000.0 * 0.05) / 20000.0  # balance * custom_risk / price
        self.assertAlmostEqual(position_size, expected_size, places=5)
        
    def test_get_positions_by_direction(self):
        """Test getting positions filtered by direction"""
        # Create a new position manager with higher risk limit for this test
        test_manager = PositionManager(
            initial_balance=10000.0,
            max_positions=3,
            max_risk_per_trade=0.05  # 5% risk per trade = $500
        )
        
        # Open multiple positions with different directions and realistic sizes
        test_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        test_manager.open_position(
            symbol='ETHUSDT',
            direction='short',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Get long positions
        long_positions = test_manager.get_positions_by_direction('long')
        
        # Verify only long positions returned
        self.assertEqual(len(long_positions), 1)
        self.assertIn('BTCUSDT', long_positions)
        self.assertNotIn('ETHUSDT', long_positions)
        
        # Get short positions
        short_positions = test_manager.get_positions_by_direction('short')
        
        # Verify only short positions returned
        self.assertEqual(len(short_positions), 1)
        self.assertIn('ETHUSDT', short_positions)
        self.assertNotIn('BTCUSDT', short_positions)
        
    def test_force_close_all_positions(self):
        """Test force closing all positions"""
        # Create a new position manager with higher risk limit for this test
        test_manager = PositionManager(
            initial_balance=10000.0,
            max_positions=3,
            max_risk_per_trade=0.05  # 5% risk per trade = $500
        )
        
        # Open multiple positions with realistic sizes
        symbols = ['BTCUSDT', 'ETHUSDT']
        for symbol in symbols:
            test_manager.open_position(
                symbol=symbol,
                direction='long',
                size=0.01,  # Realistic size
                entry_price=20000.0,
                timestamp=datetime(2023, 1, 1, 10, 0)
            )
        
        # Force close all positions
        current_prices = {'BTCUSDT': 21000.0, 'ETHUSDT': 19000.0}
        closed_trades = test_manager.force_close_all_positions(
            current_prices=current_prices,
            timestamp=datetime(2023, 1, 1, 11, 0)
        )
        
        # Verify all positions were closed
        self.assertEqual(len(closed_trades), 2)
        self.assertEqual(len(test_manager.positions), 0)
        self.assertEqual(len(test_manager.completed_trades), 2)
        
        # Verify trade details
        btc_trade = next(t for t in closed_trades if t.symbol == 'BTCUSDT')
        eth_trade = next(t for t in closed_trades if t.symbol == 'ETHUSDT')
        
        # Fix: The actual P&L is $10.00 and -$10.00, not $100.00 and -$100.00
        self.assertEqual(btc_trade.pnl, 10.0)  # (21000 - 20000) * 0.01
        self.assertEqual(eth_trade.pnl, -10.0)  # (19000 - 20000) * 0.01
        
    def test_force_close_all_positions_no_prices(self):
        """Test force closing all positions when no prices provided"""
        # Open a position
        self.position_manager.open_position(
            symbol='BTCUSDT',
            direction='long',
            size=0.01,  # Realistic size
            entry_price=20000.0,
            timestamp=datetime(2023, 1, 1, 10, 0)
        )
        
        # Force close with no prices
        closed_trades = self.position_manager.force_close_all_positions(
            current_prices={},
            timestamp=datetime(2023, 1, 1, 11, 0)
        )
        
        # Verify no positions were closed (no prices provided)
        self.assertEqual(len(closed_trades), 0)
        self.assertEqual(len(self.position_manager.positions), 1)  # Position still open

if __name__ == '__main__':
    unittest.main(verbosity=2)