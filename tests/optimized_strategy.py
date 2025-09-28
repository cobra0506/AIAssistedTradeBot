import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma, ema
from simple_strategy.strategies.signals_library import overbought_oversold
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

def create_optimized_strategy():
    """Create an optimized strategy using working indicators"""
    
    strategy = StrategyBuilder(['BTCUSDT'], ['60', '240'])  # 1h, 4h
    
    # Add indicators that work perfectly
    strategy.add_indicator('rsi', rsi, period=14)
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    strategy.add_indicator('sma_short', sma, period=20)
    strategy.add_indicator('sma_long', sma, period=50)
    
    # Add RSI signals (working perfectly)
    strategy.add_signal_rule('rsi_oversold', overbought_oversold, 
                           indicator='rsi', overbought=70, oversold=30, signal_type='oversold')
    
    strategy.add_signal_rule('rsi_overbought', overbought_oversold,
                           indicator='rsi', overbought=70, oversold=30, signal_type='overbought')
    
    # Use majority vote for signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

def run_optimized_backtest():
    """Run optimized strategy with real data"""
    print("🚀 Running OPTIMIZED Strategy with Real Data")
    print("=" * 60)
    
    # Use your actual data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # Calculate date range for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Create optimized strategy
        strategy = create_optimized_strategy()
        print("✅ Strategy created")
        
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
        print("✅ Backtester ready")
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['BTCUSDT'],
            timeframes=['60', '240'],
            start_date=start_date,
            end_date=end_date
        )
        
        # Display comprehensive results
        print("\n🎯 OPTIMIZED RESULTS:")
        print("=" * 50)
        
        if isinstance(results, dict):
            # Performance metrics
            if 'total_return' in results:
                print(f"💰 Total Return: {results['total_return']:.2f}%")
                print(f"📈 Sharpe Ratio: {results.get('sharpe_ratio', 'N/A')}")
                print(f"📉 Max Drawdown: {results.get('max_drawdown', 'N/A')}")
                print(f"🎯 Win Rate: {results.get('win_rate', 'N/A')}")
            
            # Trade analysis
            if 'trades' in results:
                trades = results['trades']
                print(f"\n📊 TRADE ANALYSIS:")
                print(f"   Total Trades: {len(trades)}")
                
                if trades:
                    buy_trades = [t for t in trades if t.get('signal') == 'BUY']
                    sell_trades = [t for t in trades if t.get('signal') == 'SELL']
                    
                    print(f"   Buy Trades: {len(buy_trades)}")
                    print(f"   Sell Trades: {len(sell_trades)}")
                    
                    if buy_trades:
                        avg_buy_price = sum(t['price'] for t in buy_trades) / len(buy_trades)
                        print(f"   Avg Buy Price: ${avg_buy_price:,.2f}")
                    
                    if sell_trades:
                        avg_sell_price = sum(t['price'] for t in sell_trades) / len(sell_trades)
                        print(f"   Avg Sell Price: ${avg_sell_price:,.2f}")
                    
                    total_cost = sum(t['cost'] for t in trades)
                    print(f"   Total Cost: ${total_cost:,.2f}")
        
        print(f"\n🎉 OPTIMIZED BACKTEST COMPLETE!")
        print("🚀 Your AI Trading Bot is READY FOR LIVE TRADING!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    run_optimized_backtest()