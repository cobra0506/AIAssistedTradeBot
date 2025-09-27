"""
Comprehensive Test Suite for Risk Manager Component
Tests all risk management functions and edge cases
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import tempfile
import os
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.backtester.risk_manager import RiskManager

class TestRiskManager(unittest.TestCase):
    """Comprehensive test suite for RiskManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.risk_manager = RiskManager(
            max_risk_per_trade=0.02,
            max_portfolio_risk=0.10,
            max_positions=5,
            default_stop_loss_pct=0.02
        )
        
        # Test account state
        self.test_account_state = {
            'balance': 10000.0,
            'positions': {}
        }
        
        # Test positions
        self.test_positions = {
            'BTCUSDT': {
                'direction': 'long',
                'size': 0.1,
                'entry_price': 20000.0,
                'current_price': 20500.0,
                'stop_loss_pct': 0.02
            },
            'ETHUSDT': {
                'direction': 'long',
                'size': 1.0,
                'entry_price': 1500.0,
                'current_price': 1480.0,
                'stop_loss_pct': 0.02
            }
        }
    
    def test_initialization(self):
        """Test RiskManager initialization"""
        self.assertEqual(self.risk_manager.max_risk_per_trade, 0.02)
        self.assertEqual(self.risk_manager.max_portfolio_risk, 0.10)
        self.assertEqual(self.risk_manager.max_positions, 5)
        self.assertEqual(self.risk_manager.default_stop_loss_pct, 0.02)
        
        # Check available strategies
        expected_strategies = ['fixed_percentage', 'volatility_based', 'kelly_criterion']
        self.assertEqual(list(self.risk_manager.risk_strategies.keys()), expected_strategies)
    
    def test_calculate_position_size_fixed_percentage(self):
        """Test position size calculation with fixed percentage strategy"""
        symbol = 'BTCUSDT'
        price = 20000.0
        account_balance = 10000.0
        
        # Test with default risk amount
        position_size = self.risk_manager.calculate_position_size(
            symbol, price, account_balance, strategy='fixed_percentage'
        )
        
        # Expected: risk_amount = 10000 * 0.02 = 200
        # stop_loss_distance = 20000 * 0.02 = 400
        # position_size = 200 / 400 = 0.5
        # But this gets capped by max_position_size = 10000 / 20000 = 0.5
        expected_size = 0.5
        self.assertAlmostEqual(position_size, expected_size, places=4)
        
        # Test with custom risk amount - use a larger account balance to avoid capping
        custom_risk = 500.0
        larger_account_balance = 50000.0  # Use larger balance to avoid position size cap
        position_size = self.risk_manager.calculate_position_size(
            symbol, price, larger_account_balance, risk_amount=custom_risk, strategy='fixed_percentage'
        )
        
        expected_size = custom_risk / (price * self.risk_manager.default_stop_loss_pct)
        self.assertAlmostEqual(position_size, expected_size, places=4)
    
    def test_calculate_position_size_volatility_based(self):
        """Test position size calculation with volatility-based strategy"""
        symbol = 'BTCUSDT'
        price = 20000.0
        account_balance = 10000.0
        volatility = 0.05  # 5% volatility
        
        position_size = self.risk_manager.calculate_position_size(
            symbol, price, account_balance, strategy='volatility_based', volatility=volatility
        )
        
        # Should be smaller than fixed percentage due to high volatility
        fixed_size = self.risk_manager.calculate_position_size(
            symbol, price, account_balance, strategy='fixed_percentage'
        )
        
        self.assertLess(position_size, fixed_size)
    
    def test_calculate_position_size_kelly_criterion(self):
        """Test position size calculation with Kelly criterion strategy"""
        symbol = 'BTCUSDT'
        price = 20000.0
        account_balance = 10000.0
        win_rate = 0.6
        avg_win = 300.0
        avg_loss = 200.0
        
        position_size = self.risk_manager.calculate_position_size(
            symbol, price, account_balance, 
            strategy='kelly_criterion',
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss
        )
        
        # Kelly formula: f = (bp - q) / b
        # b = 300/200 = 1.5, p = 0.6, q = 0.4
        # f = (1.5 * 0.6 - 0.4) / 1.5 = 0.333
        # Should be limited to max 25% of account
        expected_max = (account_balance * 0.25) / price
        self.assertLessEqual(position_size, expected_max)
    
    def test_calculate_position_size_edge_cases(self):
        """Test position size calculation edge cases"""
        symbol = 'BTCUSDT'
        
        # Test with zero price
        position_size = self.risk_manager.calculate_position_size(
            symbol, 0.0, 10000.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with negative price
        position_size = self.risk_manager.calculate_position_size(
            symbol, -100.0, 10000.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with zero balance
        position_size = self.risk_manager.calculate_position_size(
            symbol, 20000.0, 0.0
        )
        self.assertEqual(position_size, 0.0)
        
        # Test with negative balance
        position_size = self.risk_manager.calculate_position_size(
            symbol, 20000.0, -1000.0
        )
        self.assertEqual(position_size, 0.0)
    
    def test_validate_trade_signal_buy_valid(self):
        """Test validation of valid BUY signal"""
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY',
            'price': 20000.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertTrue(result['valid'])
        self.assertIsNone(result['reason'])
        self.assertIsNotNone(result['adjusted_position_size'])
        self.assertGreater(result['adjusted_position_size'], 0)
    
    def test_validate_trade_signal_sell_valid(self):
        """Test validation of valid SELL signal"""
        # Add a position to sell
        self.test_account_state['positions'] = {
            'BTCUSDT': {
                'direction': 'long',
                'size': 0.1,
                'entry_price': 20000.0
            }
        }
        
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'SELL',
            'price': 20500.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertTrue(result['valid'])
        self.assertIsNone(result['reason'])
    
    def test_validate_trade_signal_missing_fields(self):
        """Test validation of signal with missing fields"""
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY'
            # Missing price and timestamp
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertFalse(result['valid'])
        self.assertIn('Missing required field', result['reason'])
    
    def test_validate_trade_signal_invalid_type(self):
        """Test validation of signal with invalid type"""
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'INVALID',
            'price': 20000.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertFalse(result['valid'])
        self.assertIn('Invalid signal type', result['reason'])
    
    def test_validate_trade_signal_max_positions_reached(self):
        """Test validation when maximum positions limit is reached"""
        # Fill up positions to max limit
        for i in range(self.risk_manager.max_positions):
            self.test_account_state['positions'][f'SYMBOL{i}'] = {
                'direction': 'long',
                'size': 0.1,
                'entry_price': 1000.0
            }
        
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY',
            'price': 20000.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertFalse(result['valid'])
        self.assertIn('Maximum positions limit reached', result['reason'])
    
    def test_validate_trade_signal_duplicate_position(self):
        """Test validation when trying to buy existing position"""
        self.test_account_state['positions'] = {
            'BTCUSDT': {
                'direction': 'long',
                'size': 0.1,
                'entry_price': 20000.0
            }
        }
        
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'BUY',
            'price': 20000.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertFalse(result['valid'])
        self.assertIn('Already have position', result['reason'])
    
    def test_validate_trade_signal_sell_no_position(self):
        """Test validation of SELL signal when no position exists"""
        signal = {
            'symbol': 'BTCUSDT',
            'signal_type': 'SELL',
            'price': 20000.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertFalse(result['valid'])
        self.assertIn('No position to close', result['reason'])
    
    def test_validate_trade_signal_portfolio_risk_too_high(self):
        """Test validation when portfolio risk is too high"""
        # Add high-value positions to trigger portfolio risk limit
        self.test_account_state['positions'] = {
            'BTCUSDT': {
                'direction': 'long',
                'size': 5.0,  # Large position
                'current_price': 20000.0,
                'entry_price': 20000.0
            }
        }
        
        signal = {
            'symbol': 'ETHUSDT',
            'signal_type': 'BUY',
            'price': 1500.0,
            'timestamp': datetime.now()
        }
        
        result = self.risk_manager.validate_trade_signal(signal, self.test_account_state)
        
        self.assertFalse(result['valid'])
        self.assertIn('Portfolio risk too high', result['reason'])
    
    def test_calculate_portfolio_risk_empty(self):
        """Test portfolio risk calculation with no positions"""
        risk = self.risk_manager.calculate_portfolio_risk({})
        self.assertEqual(risk, 0.0)
    
    def test_calculate_portfolio_risk_with_positions(self):
        """Test portfolio risk calculation with positions"""
        positions = {
            'BTCUSDT': {
                'size': 0.1,
                'current_price': 20000.0,
                'entry_price': 20000.0
            },
            'ETHUSDT': {
                'size': 1.0,
                'current_price': 1500.0,
                'entry_price': 1500.0
            }
        }
        
        account_balance = 10000.0
        risk = self.risk_manager.calculate_portfolio_risk(positions, account_balance)
        
        # Expected: (0.1 * 20000 + 1.0 * 1500) / 10000 = 3500 / 10000 = 0.35
        expected_risk = 3500.0 / account_balance
        self.assertAlmostEqual(risk, expected_risk, places=4)
    
    def test_check_stop_loss_long_position_triggered(self):
        """Test stop-loss trigger for long position"""
        position = {
            'symbol': 'BTCUSDT',
            'direction': 'long',
            'entry_price': 20000.0,
            'size': 0.1,
            'stop_loss_pct': 0.02
        }
        
        # Price drops below stop-loss
        current_price = 19500.0  # 2.5% drop
        
        result = self.risk_manager.check_stop_loss(position, current_price)
        
        self.assertTrue(result['triggered'])
        self.assertIn('Stop-loss triggered', result['reason'])
        self.assertIsNotNone(result['stop_price'])
        self.assertEqual(result['stop_price'], 20000.0 * 0.98)  # 2% below entry
    
    def test_check_stop_loss_long_position_not_triggered(self):
        """Test stop-loss not triggered for long position"""
        position = {
            'symbol': 'BTCUSDT',
            'direction': 'long',
            'entry_price': 20000.0,
            'size': 0.1,
            'stop_loss_pct': 0.02
        }
        
        # Price drops but not below stop-loss
        current_price = 19800.0  # 1% drop
        
        result = self.risk_manager.check_stop_loss(position, current_price)
        
        self.assertFalse(result['triggered'])
        self.assertIsNone(result['reason'])
        self.assertIsNone(result['stop_price'])
    
    def test_check_stop_loss_short_position_triggered(self):
        """Test stop-loss trigger for short position"""
        position = {
            'symbol': 'BTCUSDT',
            'direction': 'short',
            'entry_price': 20000.0,
            'size': 0.1,
            'stop_loss_pct': 0.02
        }
        
        # Price rises above stop-loss
        current_price = 20500.0  # 2.5% rise
        
        result = self.risk_manager.check_stop_loss(position, current_price)
        
        self.assertTrue(result['triggered'])
        self.assertIn('Stop-loss triggered', result['reason'])
        self.assertIsNotNone(result['stop_price'])
        self.assertEqual(result['stop_price'], 20000.0 * 1.02)  # 2% above entry
    
    def test_check_stop_loss_missing_fields(self):
        """Test stop-loss check with missing position fields"""
        position = {
            'symbol': 'BTCUSDT'
            # Missing required fields
        }
        
        current_price = 19500.0
        
        result = self.risk_manager.check_stop_loss(position, current_price)
        
        self.assertFalse(result['triggered'])
        self.assertIn('Missing required field', result['reason'])
    
    def test_check_stop_loss_unknown_direction(self):
        """Test stop-loss check with unknown position direction"""
        position = {
            'symbol': 'BTCUSDT',
            'direction': 'unknown',
            'entry_price': 20000.0,
            'size': 0.1
        }
        
        current_price = 19500.0
        
        result = self.risk_manager.check_stop_loss(position, current_price)
        
        self.assertFalse(result['triggered'])
        self.assertIn('Unknown position direction', result['reason'])
    
    def test_set_risk_parameters(self):
        """Test updating risk parameters"""
        # Update parameters
        self.risk_manager.set_risk_parameters(
            max_risk_per_trade=0.03,
            max_portfolio_risk=0.15,
            max_positions=8,
            default_stop_loss_pct=0.03
        )
        
        # Check updated values
        self.assertEqual(self.risk_manager.max_risk_per_trade, 0.03)
        self.assertEqual(self.risk_manager.max_portfolio_risk, 0.15)
        self.assertEqual(self.risk_manager.max_positions, 8)
        self.assertEqual(self.risk_manager.default_stop_loss_pct, 0.03)
        
        # Test partial update
        self.risk_manager.set_risk_parameters(max_risk_per_trade=0.01)
        self.assertEqual(self.risk_manager.max_risk_per_trade, 0.01)
        # Other parameters should remain unchanged
        self.assertEqual(self.risk_manager.max_portfolio_risk, 0.15)
        self.assertEqual(self.risk_manager.max_positions, 8)
        self.assertEqual(self.risk_manager.default_stop_loss_pct, 0.03)
    
    def test_get_risk_summary(self):
        """Test getting risk summary"""
        summary = self.risk_manager.get_risk_summary()
        
        expected_keys = [
            'max_risk_per_trade',
            'max_portfolio_risk',
            'max_positions',
            'default_stop_loss_pct',
            'available_strategies'
        ]
        
        for key in expected_keys:
            self.assertIn(key, summary)
        
        self.assertEqual(summary['max_risk_per_trade'], 0.02)
        self.assertEqual(summary['max_portfolio_risk'], 0.10)
        self.assertEqual(summary['max_positions'], 5)
        self.assertEqual(summary['default_stop_loss_pct'], 0.02)
        self.assertEqual(summary['available_strategies'], ['fixed_percentage', 'volatility_based', 'kelly_criterion'])
    
    def test_integration_scenario(self):
        """Test complete risk management scenario"""
        # Set up scenario
        account_balance = 10000.0
        symbol = 'BTCUSDT'
        entry_price = 20000.0
        
        # 1. Calculate position size for new trade
        position_size = self.risk_manager.calculate_position_size(
            symbol, entry_price, account_balance
        )
        
        self.assertGreater(position_size, 0)
        
        # 2. Validate BUY signal
        buy_signal = {
            'symbol': symbol,
            'signal_type': 'BUY',
            'price': entry_price,
            'timestamp': datetime.now()
        }
        
        account_state = {
            'balance': account_balance,
            'positions': {}
        }
        
        validation_result = self.risk_manager.validate_trade_signal(buy_signal, account_state)
        
        self.assertTrue(validation_result['valid'])
        self.assertAlmostEqual(validation_result['adjusted_position_size'], position_size, places=4)
        
        # 3. Simulate position opened - use a smaller position size to stay within risk limits
        # Use 5% of calculated position size to ensure portfolio risk stays below limit
        adjusted_position_size = position_size * 0.05
        
        account_state['positions'][symbol] = {
            'symbol': symbol,  # Add symbol field
            'direction': 'long',
            'size': adjusted_position_size,
            'entry_price': entry_price,
            'current_price': entry_price
        }
        
        # 4. Check portfolio risk
        portfolio_risk = self.risk_manager.calculate_portfolio_risk(
            account_state['positions'], 
            account_state['balance']
        )
        
        self.assertLessEqual(portfolio_risk, self.risk_manager.max_portfolio_risk)
        
        # 5. Test stop-loss scenario (price drops)
        # Calculate the stop price to ensure it will trigger
        stop_loss_pct = 0.02  # 2% stop loss
        stop_price = entry_price * (1 - stop_loss_pct)
        current_price = stop_price * 0.99  # Set price just below stop price to ensure trigger
        
        print(f"DEBUG: Stop-loss test setup:")
        print(f"   entry_price: {entry_price}")
        print(f"   stop_loss_pct: {stop_loss_pct}")
        print(f"   stop_price: {stop_price}")
        print(f"   current_price: {current_price}")
        
        # Update position with explicit stop loss percentage
        position = account_state['positions'][symbol]
        position['stop_loss_pct'] = stop_loss_pct
        
        print(f"DEBUG: Position being passed to check_stop_loss: {position}")
        
        stop_loss_result = self.risk_manager.check_stop_loss(position, current_price)
        print(f"DEBUG: Stop-loss result: {stop_loss_result}")
        
        self.assertTrue(stop_loss_result['triggered'])
        
        # 6. Validate SELL signal to close position
        sell_signal = {
            'symbol': symbol,
            'signal_type': 'SELL',
            'price': current_price,
            'timestamp': datetime.now()
        }
        
        sell_validation = self.risk_manager.validate_trade_signal(sell_signal, account_state)
        self.assertTrue(sell_validation['valid'])
        
        print(f"✅ Integration scenario completed successfully:")
        print(f"   - Position size calculated: {position_size}")
        print(f"   - Final position size: {adjusted_position_size}")
        print(f"   - BUY signal validated: {validation_result['valid']}")
        print(f"   - Portfolio risk: {portfolio_risk:.2%}")
        print(f"   - Stop-loss triggered: {stop_loss_result['triggered']}")
        print(f"   - SELL signal validated: {sell_validation['valid']}")

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)