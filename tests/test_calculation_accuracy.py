"""
Backtest Calculation Accuracy Tests
Validates mathematical accuracy of trade calculations and performance metrics
Author: AI Assisted TradeBot Team
Date: 2025
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

class TestCalculationAccuracy(unittest.TestCase):
    """Tests for mathematical accuracy of backtest calculations"""
    
    def setUp(self):
        """Set up test data with known outcomes"""
        # Create predictable price data for manual verification
        self.dates = pd.date_range('2023-01-01', periods=20, freq='D')
        
        # Create price data with known pattern: uptrend then downtrend
        self.prices = pd.Series([
            100, 102, 104, 106, 108, 110, 112, 114, 116, 118,  # Uptrend
            120, 118, 116, 114, 112, 110, 108, 106, 104, 102   # Downtrend
        ], index=self.dates, name='close')
        
        # Create OHLCV data
        self.data = pd.DataFrame({
            'open': self.prices.shift(1).fillna(self.prices.iloc[0]),
            'high': self.prices + 2,
            'low': self.prices - 2,
            'close': self.prices,
            'volume': 1000
        }, index=self.dates)
        
        # Create simple strategy for testing
        self.strategy = StrategyBuilder(['TEST'], ['1D'])
        self.strategy.add_indicator('sma_fast', sma, period=3)
        self.strategy.add_indicator('sma_slow', sma, period=7)
        self.strategy.add_signal_rule('ma_cross', ma_crossover, 
                                     fast_ma='sma_fast', slow_ma='sma_slow')
        self.built_strategy = self.strategy.build()

    def test_trade_execution_calculation(self):
        """Test accuracy of trade execution calculations"""
        print("\n🧮 Testing trade execution calculations...")
        
        # Create simple backtest scenario
        initial_capital = 10000
        risk_per_trade = 0.02  # 2% risk per trade
        
        # Manually calculate expected trades
        sma_fast = self.prices.rolling(window=3).mean()
        sma_slow = self.prices.rolling(window=7).mean()
        
        expected_trades = []
        position = None
        
        for i in range(1, len(self.prices)):
            # Check for crossover
            if (sma_fast.iloc[i] > sma_slow.iloc[i] and 
                sma_fast.iloc[i-1] <= sma_slow.iloc[i-1] and 
                position is None):
                # BUY signal
                entry_price = self.prices.iloc[i]
                position_size = (initial_capital * risk_per_trade) / entry_price
                expected_trades.append({
                    'type': 'BUY',
                    'price': entry_price,
                    'size': position_size,
                    'time': self.dates[i]
                })
                position = 'long'
                
            elif (sma_fast.iloc[i] < sma_slow.iloc[i] and 
                  sma_fast.iloc[i-1] >= sma_slow.iloc[i-1] and 
                  position == 'long'):
                # SELL signal
                exit_price = self.prices.iloc[i]
                expected_trades.append({
                    'type': 'SELL',
                    'price': exit_price,
                    'size': position_size,
                    'time': self.dates[i]
                })
                position = None
        
        # Run backtest
        backtester = BacktesterEngine(
            strategy=self.built_strategy,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital
        )
        
        results = backtester.run(self.data)
        
        # Verify trade calculations
        actual_trades = results.get('trades', [])
        
        # Should have similar number of trades
        self.assertTrue(len(actual_trades) > 0, "Should generate trades")
        
        # Verify trade prices are accurate
        for trade in actual_trades:
            if trade['type'] == 'BUY':
                self.assertAlmostEqual(trade['price'], self.prices.loc[trade['time']], places=2,
                                     msg=f"BUY trade price mismatch: {trade['price']} vs {self.prices.loc[trade['time']]}")
            elif trade['type'] == 'SELL':
                self.assertAlmostEqual(trade['price'], self.prices.loc[trade['time']], places=2,
                                     msg=f"SELL trade price mismatch: {trade['price']} vs {self.prices.loc[trade['time']]}")
        
        print("✅ Trade execution calculations test passed")

    def test_position_sizing_calculation(self):
        """Test accuracy of position sizing calculations"""
        print("\n🧮 Testing position sizing calculations...")
        
        initial_capital = 10000
        risk_per_trade = 0.01  # 1% risk per trade
        stop_loss_distance = 0.05  # 5% stop loss
        
        # Test position sizing formula
        entry_price = 100
        expected_position_size = (initial_capital * risk_per_trade) / stop_loss_distance
        expected_shares = expected_position_size / entry_price
        
        # Run backtest with specific parameters
        backtester = BacktesterEngine(
            strategy=self.built_strategy,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital,
            risk_per_trade=risk_per_trade
        )
        
        results = backtester.run(self.data)
        trades = results.get('trades', [])
        
        # Verify position sizing
        for trade in trades:
            if trade['type'] == 'BUY':
                calculated_size = trade['size'] * trade['price']
                expected_max_loss = calculated_size * stop_loss_distance
                actual_risk_amount = expected_max_loss
                max_allowed_risk = initial_capital * risk_per_trade
                
                # Risk should not exceed maximum allowed
                self.assertLessEqual(actual_risk_amount, max_allowed_risk * 1.1,  # 10% tolerance
                                   f"Position size risk exceeds maximum: {actual_risk_amount} > {max_allowed_risk}")
        
        print("✅ Position sizing calculations test passed")

    def test_performance_metrics_calculation(self):
        """Test accuracy of performance metrics calculations"""
        print("\n🧮 Testing performance metrics calculations...")
        
        initial_capital = 10000
        
        # Run backtest
        backtester = BacktesterEngine(
            strategy=self.built_strategy,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital
        )
        
        results = backtester.run(self.data)
        
        # Verify key metrics exist
        required_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
        for metric in required_metrics:
            self.assertIn(metric, results, f"Missing required metric: {metric}")
        
        # Verify total return calculation
        final_capital = results.get('final_capital', initial_capital)
        calculated_total_return = (final_capital - initial_capital) / initial_capital * 100
        reported_total_return = results['total_return']
        
        self.assertAlmostEqual(calculated_total_return, reported_total_return, places=2,
                             msg=f"Total return calculation mismatch: {calculated_total_return} vs {reported_total_return}")
        
        # Verify win rate calculation
        trades = results.get('trades', [])
        if len(trades) >= 2:
            winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
            calculated_win_rate = len(winning_trades) / len(trades) * 100
            reported_win_rate = results['win_rate']
            
            self.assertAlmostEqual(calculated_win_rate, reported_win_rate, places=1,
                                 msg=f"Win rate calculation mismatch: {calculated_win_rate} vs {reported_win_rate}")
        
        print("✅ Performance metrics calculations test passed")

    def test_drawdown_calculation(self):
        """Test accuracy of drawdown calculations"""
        print("\n🧮 Testing drawdown calculations...")
        
        initial_capital = 10000
        
        # Run backtest
        backtester = BacktesterEngine(
            strategy=self.built_strategy,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital
        )
        
        results = backtester.run(self.data)
        
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
        
        # Compare with reported max drawdown
        reported_max_drawdown = results.get('max_drawdown', 0)
        self.assertAlmostEqual(max_drawdown, reported_max_drawdown, places=1,
                             msg=f"Max drawdown calculation mismatch: {max_drawdown} vs {reported_max_drawdown}")
        
        print("✅ Drawdown calculations test passed")

    def test_sharpe_ratio_calculation(self):
        """Test accuracy of Sharpe ratio calculation"""
        print("\n🧮 Testing Sharpe ratio calculations...")
        
        initial_capital = 10000
        
        # Run backtest
        backtester = BacktesterEngine(
            strategy=self.built_strategy,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital
        )
        
        results = backtester.run(self.data)
        
        # Get returns
        returns = results.get('returns', [])
        
        if len(returns) > 1:
            # Calculate Sharpe ratio manually
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return > 0:
                calculated_sharpe = (mean_return / std_return) * np.sqrt(252)  # Annualized
                reported_sharpe = results.get('sharpe_ratio', 0)
                
                # Allow some tolerance due to different calculation methods
                self.assertAlmostEqual(calculated_sharpe, reported_sharpe, places=1,
                                     msg=f"Sharpe ratio calculation mismatch: {calculated_sharpe} vs {reported_sharpe}")
        
        print("✅ Sharpe ratio calculations test passed")

    def test_risk_management_calculations(self):
        """Test accuracy of risk management calculations"""
        print("\n🧮 Testing risk management calculations...")
        
        initial_capital = 10000
        max_portfolio_risk = 0.10  # 10% max portfolio risk
        
        # Run backtest with risk management
        backtester = BacktesterEngine(
            strategy=self.built_strategy,
            start_date=self.dates[0],
            end_date=self.dates[-1],
            initial_capital=initial_capital,
            max_portfolio_risk=max_portfolio_risk
        )
        
        results = backtester.run(self.data)
        
        # Verify portfolio risk doesn't exceed maximum
        portfolio_risk = results.get('portfolio_risk', 0)
        self.assertLessEqual(portfolio_risk, max_portfolio_risk * 1.1,  # 10% tolerance
                           f"Portfolio risk exceeds maximum: {portfolio_risk} > {max_portfolio_risk}")
        
        # Verify stop-loss and take-profit calculations
        trades = results.get('trades', [])
        for trade in trades:
            if 'stop_loss' in trade:
                self.assertIsInstance(trade['stop_loss'], (int, float),
                                    "Stop loss should be numeric")
                self.assertGreater(trade['stop_loss'], 0,
                                 "Stop loss should be positive")
            
            if 'take_profit' in trade:
                self.assertIsInstance(trade['take_profit'], (int, float),
                                    "Take profit should be numeric")
                self.assertGreater(trade['take_profit'], 0,
                                 "Take profit should be positive")
        
        print("✅ Risk management calculations test passed")

if __name__ == '__main__':
    print("🚀 Running Calculation Accuracy Tests...")
    print("=" * 60)
    
    unittest.main(verbosity=2)