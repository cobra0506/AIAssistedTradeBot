"""
Unit tests for Performance Tracker
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
import json

# Add the project root to the Python path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from simple_strategy.backtester.performance_tracker import PerformanceTracker, TradeRecord, PerformanceMetrics

class TestPerformanceTracker(unittest.TestCase):
    """Comprehensive test suite for PerformanceTracker"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        self.tracker = PerformanceTracker(initial_balance=10000.0)
        self.sample_trades = self._create_sample_trades()
        self.sample_equity_curve = self._create_sample_equity_curve()
        
    def _create_sample_trades(self):
        """Create sample trade data for testing"""
        return [
            {
                'symbol': 'BTCUSDT',
                'direction': 'long',
                'entry_price': 20000.0,
                'exit_price': 21000.0,
                'size': 0.1,
                'entry_timestamp': datetime(2023, 1, 1, 10, 0),
                'exit_timestamp': datetime(2023, 1, 1, 11, 0),
                'pnl': 100.0,
                'trade_id': 'trade_001'
            },
            {
                'symbol': 'BTCUSDT',
                'direction': 'long',
                'entry_price': 20500.0,
                'exit_price': 19500.0,
                'size': 0.1,
                'entry_timestamp': datetime(2023, 1, 1, 12, 0),
                'exit_timestamp': datetime(2023, 1, 1, 13, 0),
                'pnl': -100.0,
                'trade_id': 'trade_002'
            },
            {
                'symbol': 'ETHUSDT',
                'direction': 'long',
                'entry_price': 1500.0,
                'exit_price': 1600.0,
                'size': 1.0,
                'entry_timestamp': datetime(2023, 1, 1, 14, 0),
                'exit_timestamp': datetime(2023, 1, 1, 15, 0),
                'pnl': 100.0,
                'trade_id': 'trade_003'
            }
        ]
    
    def _create_sample_equity_curve(self):
        """Create sample equity curve data for testing"""
        return [
            {'timestamp': datetime(2023, 1, 1, 10, 0), 'balance': 10000.0, 'positions_value': 0.0, 'total_equity': 10000.0},
            {'timestamp': datetime(2023, 1, 1, 11, 0), 'balance': 10100.0, 'positions_value': 0.0, 'total_equity': 10100.0},
            {'timestamp': datetime(2023, 1, 1, 12, 0), 'balance': 10100.0, 'positions_value': 2050.0, 'total_equity': 12150.0},
            {'timestamp': datetime(2023, 1, 1, 13, 0), 'balance': 10000.0, 'positions_value': 0.0, 'total_equity': 10000.0},
            {'timestamp': datetime(2023, 1, 1, 14, 0), 'balance': 10000.0, 'positions_value': 1500.0, 'total_equity': 11500.0},
            {'timestamp': datetime(2023, 1, 1, 15, 0), 'balance': 10100.0, 'positions_value': 0.0, 'total_equity': 10100.0}
        ]
    
    def test_initialization(self):
        """Test PerformanceTracker initialization"""
        # Verify initial state
        self.assertEqual(self.tracker.initial_balance, 10000.0)
        self.assertEqual(self.tracker.current_balance, 10000.0)
        self.assertEqual(len(self.tracker.trades), 0)
        self.assertEqual(len(self.tracker.equity_curve), 0)
        self.assertIsNone(self.tracker._metrics_cache)
        
    def test_record_trade_valid_trade(self):
        """Test recording a valid trade"""
        trade_data = self.sample_trades[0]
        
        # Record trade
        result = self.tracker.record_trade(trade_data)
        
        # Verify success
        self.assertTrue(result)
        self.assertEqual(len(self.tracker.trades), 1)
        
        # Verify trade details
        recorded_trade = self.tracker.trades[0]
        self.assertEqual(recorded_trade.symbol, 'BTCUSDT')
        self.assertEqual(recorded_trade.pnl, 100.0)
        self.assertEqual(recorded_trade.direction, 'long')
        
        # Verify balance was updated
        self.assertEqual(self.tracker.current_balance, 10100.0)
        
        # Verify cache was invalidated
        self.assertIsNone(self.tracker._metrics_cache)
    
    def test_record_trade_missing_required_field(self):
        """Test recording trade with missing required field"""
        # Create trade with missing field
        invalid_trade = self.sample_trades[0].copy()
        del invalid_trade['symbol']
        
        # Attempt to record
        result = self.tracker.record_trade(invalid_trade)
        
        # Verify failure
        self.assertFalse(result)
        self.assertEqual(len(self.tracker.trades), 0)
        self.assertEqual(self.tracker.current_balance, 10000.0)  # Balance unchanged
    
    def test_record_multiple_trades(self):
        """Test recording multiple trades"""
        # Record all sample trades
        for trade_data in self.sample_trades:
            result = self.tracker.record_trade(trade_data)
            self.assertTrue(result)
        
        # Verify all trades recorded
        self.assertEqual(len(self.tracker.trades), 3)
        
        # Verify final balance (10000 + 100 - 100 + 100 = 10100)
        self.assertEqual(self.tracker.current_balance, 10100.0)
        
        # Verify trade details
        self.assertEqual(self.tracker.trades[0].symbol, 'BTCUSDT')
        self.assertEqual(self.tracker.trades[1].symbol, 'BTCUSDT')
        self.assertEqual(self.tracker.trades[2].symbol, 'ETHUSDT')
    
    def test_update_equity(self):
        """Test updating equity curve"""
        timestamp = datetime(2023, 1, 1, 10, 0)
        
        # Update equity
        self.tracker.update_equity(timestamp, 10500.0, 500.0)
        
        # Verify equity curve updated
        self.assertEqual(len(self.tracker.equity_curve), 1)
        
        equity_point = self.tracker.equity_curve[0]
        self.assertEqual(equity_point['timestamp'], timestamp)
        self.assertEqual(equity_point['balance'], 10500.0)
        self.assertEqual(equity_point['positions_value'], 500.0)
        self.assertEqual(equity_point['total_equity'], 11000.0)
        
        # Verify cache was invalidated
        self.assertIsNone(self.tracker._metrics_cache)
    
    def test_calculate_metrics_no_trades(self):
        """Test calculating metrics with no trades"""
        metrics = self.tracker.calculate_metrics()
        
        # Verify basic metrics
        self.assertEqual(metrics.initial_balance, 10000.0)
        self.assertEqual(metrics.final_balance, 10000.0)
        self.assertEqual(metrics.total_return, 0.0)
        self.assertEqual(metrics.total_trades, 0)
        self.assertEqual(metrics.winning_trades, 0)
        self.assertEqual(metrics.losing_trades, 0)
        self.assertEqual(metrics.win_rate, 0.0)
    
    def test_calculate_metrics_with_trades(self):
        """Test calculating metrics with trades"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Add equity curve data
        for equity_point in self.sample_equity_curve:
            self.tracker.update_equity(
                equity_point['timestamp'],
                equity_point['balance'],
                equity_point['positions_value']
            )
        
        # Calculate metrics
        metrics = self.tracker.calculate_metrics()
        
        # Verify basic metrics
        self.assertEqual(metrics.initial_balance, 10000.0)
        self.assertEqual(metrics.final_balance, 10100.0)
        self.assertEqual(metrics.total_return, 0.01)  # 1% return
        self.assertEqual(metrics.total_return_pct, 1.0)
        
        # Verify trade statistics
        self.assertEqual(metrics.total_trades, 3)
        self.assertEqual(metrics.winning_trades, 2)
        self.assertEqual(metrics.losing_trades, 1)
        self.assertAlmostEqual(metrics.win_rate, 2/3, places=5)
        
        # Verify profit metrics
        self.assertEqual(metrics.gross_profit, 200.0)  # 100 + 100
        self.assertEqual(metrics.gross_loss, 100.0)
        self.assertEqual(metrics.net_profit, 100.0)
        self.assertEqual(metrics.avg_win, 100.0)
        self.assertEqual(metrics.avg_loss, 100.0)
        self.assertEqual(metrics.profit_factor, 2.0)
    
    def test_calculate_metrics_caching(self):
        """Test metrics caching functionality"""
        # Record a trade
        self.tracker.record_trade(self.sample_trades[0])
        
        # Calculate metrics (should create cache)
        metrics1 = self.tracker.calculate_metrics()
        self.assertIsNotNone(self.tracker._metrics_cache)
        self.assertIsNotNone(self.tracker._last_calculation_time)
        
        # Calculate again (should use cache)
        metrics2 = self.tracker.calculate_metrics()
        self.assertEqual(metrics1, metrics2)
        
        # Record another trade (should invalidate cache)
        self.tracker.record_trade(self.sample_trades[1])
        self.assertIsNone(self.tracker._metrics_cache)
    
    def test_get_equity_curve(self):
        """Test getting equity curve as DataFrame"""
        # Add equity curve data
        for equity_point in self.sample_equity_curve:
            self.tracker.update_equity(
                equity_point['timestamp'],
                equity_point['balance'],
                equity_point['positions_value']
            )
        
        # Get equity curve
        equity_df = self.tracker.get_equity_curve()
        
        # Verify DataFrame structure
        self.assertIsInstance(equity_df, pd.DataFrame)
        self.assertEqual(len(equity_df), 6)
        self.assertIn('balance', equity_df.columns)
        self.assertIn('total_equity', equity_df.columns)
        self.assertIn('positions_value', equity_df.columns)
        
        # Verify index is timestamp
        self.assertTrue(isinstance(equity_df.index, pd.DatetimeIndex))
    
    def test_get_equity_curve_empty(self):
        """Test getting equity curve when empty"""
        equity_df = self.tracker.get_equity_curve()
        self.assertTrue(equity_df.empty)
    
    def test_get_trade_history(self):
        """Test getting trade history as DataFrame"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Get trade history
        trades_df = self.tracker.get_trade_history()
        
        # Verify DataFrame structure
        self.assertIsInstance(trades_df, pd.DataFrame)
        self.assertEqual(len(trades_df), 3)
        self.assertIn('symbol', trades_df.columns)
        self.assertIn('pnl', trades_df.columns)
        self.assertIn('duration_minutes', trades_df.columns)
        
        # Verify trade data
        self.assertEqual(trades_df['symbol'].iloc[0], 'BTCUSDT')
        self.assertEqual(trades_df['pnl'].iloc[0], 100.0)
    
    def test_get_trade_history_empty(self):
        """Test getting trade history when empty"""
        trades_df = self.tracker.get_trade_history()
        self.assertTrue(trades_df.empty)
    
    def test_get_symbol_performance(self):
        """Test getting performance breakdown by symbol"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Get symbol performance
        symbol_perf = self.tracker.get_symbol_performance()
        
        # Verify structure
        self.assertIn('BTCUSDT', symbol_perf)
        self.assertIn('ETHUSDT', symbol_perf)
        
        # Verify BTCUSDT performance
        btc_stats = symbol_perf['BTCUSDT']
        self.assertEqual(btc_stats['total_trades'], 2)
        self.assertEqual(btc_stats['winning_trades'], 1)
        self.assertEqual(btc_stats['total_pnl'], 0.0)  # 100 - 100
        self.assertEqual(btc_stats['win_rate'], 0.5)
        
        # Verify ETHUSDT performance
        eth_stats = symbol_perf['ETHUSDT']
        self.assertEqual(eth_stats['total_trades'], 1)
        self.assertEqual(eth_stats['winning_trades'], 1)
        self.assertEqual(eth_stats['total_pnl'], 100.0)
        self.assertEqual(eth_stats['win_rate'], 1.0)
    
    def test_get_symbol_performance_empty(self):
        """Test getting symbol performance when no trades"""
        symbol_perf = self.tracker.get_symbol_performance()
        self.assertEqual(len(symbol_perf), 0)
    
    def test_get_drawdown_periods(self):
        """Test getting drawdown periods"""
        # Create equity curve with drawdown
        equity_with_drawdown = [
            {'timestamp': datetime(2023, 1, 1, 10, 0), 'balance': 10000.0, 'positions_value': 0.0, 'total_equity': 10000.0},
            {'timestamp': datetime(2023, 1, 1, 11, 0), 'balance': 11000.0, 'positions_value': 0.0, 'total_equity': 11000.0},  # Peak
            {'timestamp': datetime(2023, 1, 1, 12, 0), 'balance': 10500.0, 'positions_value': 0.0, 'total_equity': 10500.0},  # Drawdown
            {'timestamp': datetime(2023, 1, 1, 13, 0), 'balance': 9000.0, 'positions_value': 0.0, 'total_equity': 9000.0},   # Trough
            {'timestamp': datetime(2023, 1, 1, 14, 0), 'balance': 9500.0, 'positions_value': 0.0, 'total_equity': 9500.0},   # Recovery
            {'timestamp': datetime(2023, 1, 1, 15, 0), 'balance': 12000.0, 'positions_value': 0.0, 'total_equity': 12000.0}   # New peak
        ]
        
        # Add equity curve data
        for equity_point in equity_with_drawdown:
            self.tracker.update_equity(
                equity_point['timestamp'],
                equity_point['balance'],
                equity_point['positions_value']
            )
        
        # Get drawdown periods
        drawdown_df = self.tracker.get_drawdown_periods()
        
        # Verify structure
        self.assertIsInstance(drawdown_df, pd.DataFrame)
        
        # We should have exactly one drawdown period
        self.assertEqual(len(drawdown_df), 1)
        
        # Verify drawdown details
        drawdown = drawdown_df.iloc[0]
        self.assertEqual(drawdown['peak_value'], 11000.0)
        self.assertEqual(drawdown['trough_value'], 9000.0)
        self.assertEqual(drawdown['drawdown_amount'], 2000.0)
        self.assertAlmostEqual(drawdown['drawdown_pct'], 18.18, places=2)  # 2000/11000
        
        # Verify duration
        expected_duration = datetime(2023, 1, 1, 14, 0) - datetime(2023, 1, 1, 11, 0)
        self.assertEqual(drawdown['duration'], expected_duration)
    
    def test_export_results_json(self):
        """Test exporting results to JSON"""
        # Record sample trades and equity data
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        for equity_point in self.sample_equity_curve:
            self.tracker.update_equity(
                equity_point['timestamp'],
                equity_point['balance'],
                equity_point['positions_value']
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Export results
            result = self.tracker.export_results(temp_path)
            self.assertTrue(result)
            
            # Verify file exists and contains data
            self.assertTrue(os.path.exists(temp_path))
            
            with open(temp_path, 'r') as f:
                exported_data = json.load(f)
            
            self.assertIn('metrics', exported_data)
            self.assertIn('trades', exported_data)
            self.assertIn('equity_curve', exported_data)
            self.assertEqual(len(exported_data['trades']), 3)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_results_csv(self):
        """Test exporting results to CSV/Excel"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xlsx', delete=False) as f:
            temp_path = f.name
        
        try:
            # Export results
            result = self.tracker.export_results(temp_path)
            self.assertTrue(result)
            
            # Verify file exists
            self.assertTrue(os.path.exists(temp_path))
            
            # Verify it's a valid Excel file
            df_metrics = pd.read_excel(temp_path, sheet_name='Metrics')
            df_trades = pd.read_excel(temp_path, sheet_name='Trades')
            
            self.assertEqual(len(df_metrics), 1)
            self.assertEqual(len(df_trades), 3)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_export_results_unsupported_format(self):
        """Test exporting results with unsupported format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        
        try:
            result = self.tracker.export_results(temp_path)
            self.assertFalse(result)
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_calculate_drawdown_metrics(self):
        """Test drawdown metrics calculation"""
        # Create equity curve with known drawdown
        equity_data = [
            {'timestamp': datetime(2023, 1, 1, 10, 0), 'balance': 10000.0, 'positions_value': 0.0, 'total_equity': 10000.0},
            {'timestamp': datetime(2023, 1, 1, 11, 0), 'balance': 12000.0, 'positions_value': 0.0, 'total_equity': 12000.0},  # Peak
            {'timestamp': datetime(2023, 1, 1, 12, 0), 'balance': 9000.0, 'positions_value': 0.0, 'total_equity': 9000.0},   # 25% drawdown
            {'timestamp': datetime(2023, 1, 1, 13, 0), 'balance': 11000.0, 'positions_value': 0.0, 'total_equity': 11000.0}   # Recovery
        ]
        
        for equity_point in equity_data:
            self.tracker.update_equity(
                equity_point['timestamp'],
                equity_point['balance'],
                equity_point['positions_value']
            )
        
        # Calculate drawdown metrics
        max_dd, max_dd_pct, avg_dd = self.tracker._calculate_drawdown_metrics()
        
        # Verify calculations
        self.assertAlmostEqual(max_dd, 0.25, places=5)  # 25% drawdown
        self.assertAlmostEqual(max_dd_pct, 25.0, places=2)
        self.assertGreater(avg_dd, 0)
    
    def test_calculate_risk_metrics(self):
        """Test risk metrics calculation"""
        # Create equity curve with varying returns
        equity_data = [
            {'timestamp': datetime(2023, 1, 1, 10, 0), 'balance': 10000.0, 'positions_value': 0.0, 'total_equity': 10000.0},
            {'timestamp': datetime(2023, 1, 1, 11, 0), 'balance': 10100.0, 'positions_value': 0.0, 'total_equity': 10100.0},
            {'timestamp': datetime(2023, 1, 1, 12, 0), 'balance': 10200.0, 'positions_value': 0.0, 'total_equity': 10200.0},
            {'timestamp': datetime(2023, 1, 1, 13, 0), 'balance': 10100.0, 'positions_value': 0.0, 'total_equity': 10100.0}
        ]
        
        for equity_point in equity_data:
            self.tracker.update_equity(
                equity_point['timestamp'],
                equity_point['balance'],
                equity_point['positions_value']
            )
        
        # Calculate risk metrics
        sharpe, sortino = self.tracker._calculate_risk_metrics(risk_free_rate=0.02)
        
        # Verify metrics are calculated (values will vary based on data)
        self.assertIsInstance(sharpe, float)
        self.assertIsInstance(sortino, float)
    
    def test_calculate_consecutive_trades(self):
        """Test consecutive trades calculation"""
        # Create trades with specific pattern: Win, Win, Loss, Loss, Win
        trades_data = [
            {**self.sample_trades[0], 'pnl': 100.0, 'trade_id': 'win1'},   # Win
            {**self.sample_trades[0], 'pnl': 50.0, 'trade_id': 'win2'},    # Win
            {**self.sample_trades[0], 'pnl': -75.0, 'trade_id': 'loss1'},  # Loss
            {**self.sample_trades[0], 'pnl': -25.0, 'trade_id': 'loss2'},  # Loss
            {**self.sample_trades[0], 'pnl': 150.0, 'trade_id': 'win3'}    # Win
        ]
        
        for trade_data in trades_data:
            self.tracker.record_trade(trade_data)
        
        # Calculate consecutive trades
        max_wins, max_losses = self.tracker._calculate_consecutive_trades()
        
        # Verify results
        self.assertEqual(max_wins, 2)
        self.assertEqual(max_losses, 2)
    
    def test_calculate_expectancy(self):
        """Test trade expectancy calculation"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Calculate expectancy
        expectancy = self.tracker._calculate_expectancy()
        
        # Manual calculation: (2/3 * 100) - (1/3 * 100) = 66.67 - 33.33 = 33.34
        expected_expectancy = (2/3 * 100) - (1/3 * 100)
        self.assertAlmostEqual(expectancy, expected_expectancy, places=2)
    
    def test_calculate_avg_trade_duration(self):
        """Test average trade duration calculation"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Calculate average duration
        avg_duration = self.tracker._calculate_avg_trade_duration()
        
        # All sample trades have 1 hour duration
        expected_duration = timedelta(hours=1)
        self.assertEqual(avg_duration, expected_duration)
    
    def test_reset(self):
        """Test resetting performance tracker"""
        # Add some data
        self.tracker.record_trade(self.sample_trades[0])
        self.tracker.update_equity(datetime.now(), 10500.0, 500.0)
        
        # Verify data exists
        self.assertGreater(len(self.tracker.trades), 0)
        self.assertGreater(len(self.tracker.equity_curve), 0)
        
        # Reset
        self.tracker.reset()
        
        # Verify reset
        self.assertEqual(len(self.tracker.trades), 0)
        self.assertEqual(len(self.tracker.equity_curve), 0)
        self.assertEqual(self.tracker.current_balance, 10000.0)
        self.assertIsNone(self.tracker._metrics_cache)
    
    def test_get_summary(self):
        """Test getting performance summary"""
        # Record sample trades
        for trade_data in self.sample_trades:
            self.tracker.record_trade(trade_data)
        
        # Get summary
        summary = self.tracker.get_summary()
        
        # Verify structure
        self.assertIsInstance(summary, dict)
        self.assertIn('total_return_pct', summary)
        self.assertIn('final_balance', summary)
        self.assertIn('total_trades', summary)
        self.assertIn('win_rate_pct', summary)
        
        # Verify values are formatted as strings
        self.assertIsInstance(summary['total_return_pct'], str)
        self.assertIsInstance(summary['final_balance'], str)
        self.assertIsInstance(summary['win_rate_pct'], str)

if __name__ == '__main__':
    unittest.main(verbosity=2)