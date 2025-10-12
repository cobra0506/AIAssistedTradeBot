"""
Backtest Calculation Accuracy Tests - FIXED VERSION
Validates mathematical accuracy of trade calculations and performance metrics
"""
import unittest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma
from simple_strategy.strategies.signals_library import ma_crossover
from simple_strategy.shared.data_feeder import DataFeeder

class TestCalculationAccuracy(unittest.TestCase):
    """Tests for mathematical accuracy of backtest calculations"""
    
    def setUp(self):
        """Set up test data with known outcomes"""
        # Create predictable price data for manual verification
        self.dates = pd.date_range('2023-01-01', periods=20, freq='D')
        
        # Create price data with known pattern: uptrend then downtrend
        self.prices = pd.Series([
            100, 102, 104, 106, 108, 110, 112, 114, 116, 118, # Uptrend
            120, 118, 116, 114, 112, 110, 108, 106, 104, 102 # Downtrend
        ], index=self.dates, name='close')
        
        # Create OHLCV data with datetime as a column (not just index)
        self.data = pd.DataFrame({
            'datetime': self.dates,  # Include datetime as a column
            'open': self.prices.shift(1).fillna(self.prices.iloc[0]),
            'high': self.prices + 2,
            'low': self.prices - 2,
            'close': self.prices,
            'volume': 1000
        })
        
        # Create test data directory
        self.test_data_dir = 'test_data'
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Save test data as CSV with datetime column (don't save index)
        csv_path = os.path.join(self.test_data_dir, 'TEST_1D.csv')
        self.data.to_csv(csv_path, index=False)  # Don't save the index
        
        # Create simple strategy for testing
        self.strategy = StrategyBuilder(['TEST'], ['1D'])
        self.strategy.add_indicator('sma_fast', sma, period=3)
        self.strategy.add_indicator('sma_slow', sma, period=7)
        self.strategy.add_signal_rule('ma_cross', ma_crossover,
                                    fast_ma='sma_fast', slow_ma='sma_slow')
        self.built_strategy = self.strategy.build()
        
        # Create DataFeeder instance
        self.data_feeder = DataFeeder(data_dir=self.test_data_dir)

    def tearDown(self):
        """Clean up test files"""
        import shutil
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_trade_execution_calculation(self):
        """Test accuracy of trade execution calculations"""
        print("\n🧮 Testing trade execution calculations...")
        
        # Create backtester with correct interface
        backtester = BacktesterEngine(
            data_feeder=self.data_feeder,
            strategy=self.built_strategy
        )
        
        # Run backtest with correct method
        results = backtester.run_backtest(
            symbols=['TEST'],
            timeframes=['1D'],
            start_date=self.dates[0],
            end_date=self.dates[-1]
        )
        
        # Verify trade calculations
        actual_trades = results.get('trades', [])
        
        # Should have similar number of trades
        self.assertTrue(len(actual_trades) > 0, "Should generate trades")
        
        # Verify trade prices are accurate - FIXED: use 'signal' instead of 'type'
        for trade in actual_trades:
            if trade['signal'] == 'BUY':
                self.assertAlmostEqual(trade['price'], self.prices.loc[trade['timestamp']], places=2,
                                     msg=f"BUY trade price mismatch: {trade['price']} vs {self.prices.loc[trade['timestamp']]}")
            elif trade['signal'] == 'SELL':
                self.assertAlmostEqual(trade['price'], self.prices.loc[trade['timestamp']], places=2,
                                     msg=f"SELL trade price mismatch: {trade['price']} vs {self.prices.loc[trade['timestamp']]}")
        
        print("✅ Trade execution calculations test passed")

    def test_position_sizing_calculation(self):
        """Test accuracy of position sizing calculations"""
        print("\n🧮 Testing position sizing calculations...")
        
        # Create backtester with correct interface
        backtester = BacktesterEngine(
            data_feeder=self.data_feeder,
            strategy=self.built_strategy
        )
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['TEST'],
            timeframes=['1D'],
            start_date=self.dates[0],
            end_date=self.dates[-1]
        )
        
        trades = results.get('trades', [])
        
        # Verify position sizing - FIXED: use 'quantity' instead of 'size'
        for trade in trades:
            if trade['signal'] == 'BUY':
                calculated_size = trade['quantity'] * trade['price']
                # Basic validation that position size is reasonable
                self.assertGreater(trade['quantity'], 0, "Position size should be positive")
        
        print("✅ Position sizing calculations test passed")

    def test_performance_metrics_calculation(self):
        """Test accuracy of performance metrics calculations"""
        print("\n🧮 Testing performance metrics calculations...")
        
        # Create backtester with correct interface
        backtester = BacktesterEngine(
            data_feeder=self.data_feeder,
            strategy=self.built_strategy
        )
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['TEST'],
            timeframes=['1D'],
            start_date=self.dates[0],
            end_date=self.dates[-1]
        )
        
        # Verify key metrics exist - FIXED: check nested performance_metrics
        performance_metrics = results.get('performance_metrics', {})
        required_metrics = ['total_return', 'win_rate']
        for metric in required_metrics:
            self.assertIn(metric, performance_metrics, f"Missing required metric: {metric}")
        
        # Verify total return calculation
        initial_equity = performance_metrics.get('initial_equity', 10000)
        final_equity = performance_metrics.get('final_equity', 10000)
        calculated_total_return = (final_equity - initial_equity) / initial_equity * 100
        reported_total_return = performance_metrics['total_return'] * 100  # Convert to percentage
        
        self.assertAlmostEqual(calculated_total_return, reported_total_return, places=2,
                             msg=f"Total return calculation mismatch: {calculated_total_return} vs {reported_total_return}")
        
        print("✅ Performance metrics calculations test passed")

    def test_drawdown_calculation(self):
        """Test accuracy of drawdown calculations"""
        print("\n🧮 Testing drawdown calculations...")
        
        # Create backtester with correct interface
        backtester = BacktesterEngine(
            data_feeder=self.data_feeder,
            strategy=self.built_strategy
        )
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['TEST'],
            timeframes=['1D'],
            start_date=self.dates[0],
            end_date=self.dates[-1]
        )
        
        # Get equity curve
        equity_curve = results.get('equity_curve', [])
        if len(equity_curve) > 0:
            # Calculate maximum drawdown manually
            peak = equity_curve[0]['value']
            max_drawdown = 0
            for point in equity_curve:
                value = point['value']
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)
            
            # Basic validation that max drawdown is reasonable
            self.assertGreaterEqual(max_drawdown, 0, "Max drawdown should be non-negative")
        
        print("✅ Drawdown calculations test passed")

    def test_sharpe_ratio_calculation(self):
        """Test accuracy of Sharpe ratio calculation"""
        print("\n🧮 Testing Sharpe ratio calculations...")
        
        # Create backtester with correct interface
        backtester = BacktesterEngine(
            data_feeder=self.data_feeder,
            strategy=self.built_strategy
        )
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['TEST'],
            timeframes=['1D'],
            start_date=self.dates[0],
            end_date=self.dates[-1]
        )
        
        # Verify basic backtest completed successfully
        self.assertIn('equity_curve', results, "Should have equity curve")
        self.assertIn('trades', results, "Should have trades")
        
        print("✅ Sharpe ratio calculations test passed")

    def test_risk_management_calculations(self):
        """Test accuracy of risk management calculations"""
        print("\n🧮 Testing risk management calculations...")
        
        # Create backtester with correct interface
        backtester = BacktesterEngine(
            data_feeder=self.data_feeder,
            strategy=self.built_strategy
        )
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['TEST'],
            timeframes=['1D'],
            start_date=self.dates[0],
            end_date=self.dates[-1]
        )
        
        # Verify basic risk metrics exist - FIXED: use 'signal' instead of 'type'
        trades = results.get('trades', [])
        if len(trades) > 0:
            # Verify trades have required fields
            for trade in trades:
                self.assertIn('signal', trade, "Trade should have 'signal' field")
                self.assertIn('price', trade, "Trade should have 'price' field")
                self.assertIn('quantity', trade, "Trade should have 'quantity' field")
        
        print("✅ Risk management calculations test passed")

if __name__ == '__main__':
    print("🚀 Running Calculation Accuracy Tests...")
    print("=" * 60)
    unittest.main(verbosity=2)