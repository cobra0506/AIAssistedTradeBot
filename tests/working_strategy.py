import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema, rsi
from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

def create_working_strategy_with_manual_signals():
    """Create a strategy that manually handles signal logic"""
    
    strategy_content = '''# Working Strategy with Manual Signal Logic
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema, rsi
from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold

def create_working_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Working strategy with manual signal logic
    Strategy Logic:
    - EMA crossover for trend following
    - RSI for overbought/oversold conditions
    - Manual signal generation to avoid parameter issues
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators that we KNOW work perfectly
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    strategy.add_indicator('rsi', rsi, period=14)
    
    # Add signal rules - let's try the correct way
    strategy.add_signal_rule('ema_cross', ma_crossover)
    strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# working_strategy = create_working_strategy()
'''
    
    try:
        # Make sure the directory exists
        os.makedirs('simple_strategy/strategies', exist_ok=True)
        
        with open('simple_strategy/strategies/Strategy_Working.py', 'w') as f:
            f.write(strategy_content)
        
        print("✅ Created Working Strategy")
        print("📁 File saved to: simple_strategy/strategies/Strategy_Working.py")
        
    except Exception as e:
        print(f"❌ Error creating strategy file: {e}")

def test_working_strategy():
    """Test the working strategy"""
    print("🚀 Testing Working Strategy...")
    print("=" * 50)
    
    # Use your actual data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # Calculate date range for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Import the working strategy
        from simple_strategy.strategies.Strategy_Working import create_working_strategy
        
        # Create the working strategy
        strategy = create_working_strategy()
        print("✅ Working strategy created successfully!")
        
        # Initialize components
        data_feeder = DataFeeder(data_dir=data_dir)
        risk_manager = RiskManager(max_risk_per_trade=0.02, max_portfolio_risk=0.10)
        
        # Create backtester
        backtester = BacktesterEngine(
            data_feeder=data_feeder,
            strategy=strategy,
            risk_manager=risk_manager,
            config={"processing_mode": "sequential"}
        )
        print("✅ Backtester created successfully!")
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['BTCUSDT'],
            timeframes=['60', '240'],
            start_date=start_date,
            end_date=end_date
        )
        
        print("✅ Backtest completed successfully!")
        
        # Display results
        print("\n📊 WORKING STRATEGY RESULTS:")
        print("=" * 50)
        
        if isinstance(results, dict):
            if 'trades' in results:
                trades = results['trades']
                print(f"Total Trades: {len(trades)}")
                
                if trades:
                    buy_trades = [t for t in trades if t.get('signal') == 'BUY']
                    sell_trades = [t for t in trades if t.get('signal') == 'SELL']
                    
                    print(f"Buy Trades: {len(buy_trades)}")
                    print(f"Sell Trades: {len(sell_trades)}")
                    
                    if buy_trades:
                        avg_buy_price = sum(t['price'] for t in buy_trades) / len(buy_trades)
                        print(f"Avg Buy Price: ${avg_buy_price:,.2f}")
                    
                    if sell_trades:
                        avg_sell_price = sum(t['price'] for t in sell_trades) / len(sell_trades)
                        print(f"Avg Sell Price: ${avg_sell_price:,.2f}")
                else:
                    print("No trades executed (all HOLD signals)")
            
            # Check for performance metrics
            if 'total_return' in results:
                print(f"\nPerformance Metrics:")
                print(f"Total Return: {results['total_return']:.2f}%")
                print(f"Sharpe Ratio: {results.get('sharpe_ratio', 'N/A')}")
                print(f"Max Drawdown: {results.get('max_drawdown', 'N/A')}%")
                print(f"Win Rate: {results.get('win_rate', 'N/A')}%")
        
        print(f"\n🎉 WORKING STRATEGY TEST COMPLETE!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == '__main__':
    print("🎯 Creating and Testing Working Strategy...")
    print("=" * 60)
    
    create_working_strategy_with_manual_signals()
    print()
    test_working_strategy()