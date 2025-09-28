import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma, ema
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

def create_simple_working_strategy():
    """Create a simple strategy using only working indicators"""
    
    strategy = StrategyBuilder(['BTCUSDT'], ['60', '240'])  # 1h, 4h
    
    # Add indicators that we know work
    strategy.add_indicator('rsi', rsi, period=14)
    strategy.add_indicator('sma_short', sma, period=20)
    strategy.add_indicator('sma_long', sma, period=50)
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    
    # Add signals that we know work
    strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                           indicator='rsi', overbought=70, oversold=30)
    
    strategy.add_signal_rule('ma_crossover', ma_crossover,
                           fast_period=20, slow_period=50)
    
    # Use majority vote for signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

def test_simple_strategy():
    """Test the simple working strategy with real data"""
    print("🚀 Testing Simple Working Strategy with Real Data")
    print("=" * 60)
    
    # Use your actual data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    print(f"📁 Using data directory: {data_dir}")
    
    # Calculate date range for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Create simple strategy
        strategy = create_simple_working_strategy()
        print("✅ Strategy created successfully")
        
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
        print("✅ BacktesterEngine created successfully")
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['BTCUSDT'],
            timeframes=['60', '240'],  # 1h, 4h
            start_date=start_date,
            end_date=end_date
        )
        print("✅ Backtest completed successfully!")
        
        # Display results
        print("\n📊 BACKTEST RESULTS:")
        print("=" * 40)
        
        if isinstance(results, dict):
            # Check for performance metrics
            if 'total_return' in results:
                print(f"💰 Total Return: {results['total_return']:.2f}%")
                print(f"📈 Sharpe Ratio: {results.get('sharpe_ratio', 'N/A')}")
                print(f"📉 Max Drawdown: {results.get('max_drawdown', 'N/A')}")
                print(f"🎯 Win Rate: {results.get('win_rate', 'N/A')}")
                print(f"📊 Total Trades: {results.get('total_trades', 0)}")
            
            # Check for trades
            if 'trades' in results and results['trades']:
                print(f"\n📈 TRADES EXECUTED: {len(results['trades'])}")
                for i, trade in enumerate(results['trades'][:5]):  # Show first 5 trades
                    print(f"   Trade {i+1}: {trade}")
                if len(results['trades']) > 5:
                    print(f"   ... and {len(results['trades']) - 5} more trades")
            else:
                print("\n📈 TRADES EXECUTED: 0")
            
            # Check for signals summary
            if 'signals' in results:
                buy_signals = sum(1 for s in results['signals'] 
                                 if any(signal.get('BTCUSDT', {}).get('60') == 'BUY' 
                                       or signal.get('BTCUSDT', {}).get('240') == 'BUY' 
                                       for signal in [s['signals']]))
                sell_signals = sum(1 for s in results['signals'] 
                                  if any(signal.get('BTCUSDT', {}).get('60') == 'SELL' 
                                        or signal.get('BTCUSDT', {}).get('240') == 'SELL' 
                                        for signal in [s['signals']]))
                
                print(f"\n📊 SIGNALS SUMMARY:")
                print(f"   BUY signals: {buy_signals}")
                print(f"   SELL signals: {sell_signals}")
                print(f"   HOLD signals: {len(results['signals']) - buy_signals - sell_signals}")
        
        print(f"\n🎉 SUCCESS! Strategy test completed with real data!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == '__main__':
    test_simple_strategy()