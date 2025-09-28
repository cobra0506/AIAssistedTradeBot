import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import srsi  # Stochastic RSI
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

def create_srsi_multi_timeframe_strategy():
    """
    Multi-timeframe Stochastic RSI Strategy:
    
    LONG ENTRY: 
    - 15m SRSI < 20
    - 5m SRSI < 20  
    - 1m SRSI < 20
    
    LONG EXIT:
    - 15m SRSI > 80
    
    SHORT ENTRY:
    - 15m SRSI > 80
    - 5m SRSI > 80
    - 1m SRSI > 80
    
    SHORT EXIT:
    - 15m SRSI < 20
    """
    
    # Use all symbols and timeframes needed
    symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT']
    timeframes = ['1', '5', '15']  # 1m, 5m, 15m data
    
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add SRSI indicators for each timeframe
    strategy.add_indicator('srsi_1m', srsi, period=14, timeframe='1')
    strategy.add_indicator('srsi_5m', srsi, period=14, timeframe='5') 
    strategy.add_indicator('srsi_15m', srsi, period=14, timeframe='15')
    
    # Note: We'll need to implement custom signal logic since the built-in
    # signals don't support multi-timeframe conditions
    
    return strategy.build()

def test_srsi_strategy():
    """Test the SRSI multi-timeframe strategy"""
    print("🎯 Testing SRSI Multi-Timeframe Strategy")
    print("=" * 60)
    
    # Use your actual data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # Check if we have the required timeframe data
    required_files = ['BTCUSDT_1.csv', 'BTCUSDT_5.csv', 'BTCUSDT_15.csv']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(data_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required data files: {missing_files}")
        print("Please collect 1m, 5m, and 15m data for all symbols")
        return
    
    # Calculate date range for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Create SRSI strategy
        strategy = create_srsi_multi_timeframe_strategy()
        print("✅ Strategy created")
        
        # Initialize components with realistic trading costs
        data_feeder = DataFeeder(data_dir=data_dir)
        risk_manager = RiskManager(
            max_risk_per_trade=0.02, 
            max_portfolio_risk=0.10,
            # Add realistic trading costs
            commission=0.001,  # 0.1% commission
            slippage=0.0005   # 0.05% slippage
        )
        
        # Create backtester
        backtester = BacktesterEngine(
            data_feeder=data_feeder,
            strategy=strategy,
            risk_manager=risk_manager,
            config={
                "processing_mode": "sequential",
                "include_trading_costs": True,
                "realistic_execution": True
            }
        )
        print("✅ Backtester ready with realistic trading costs")
        
        # Run backtest
        results = backtester.run_backtest(
            symbols=['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT'],
            timeframes=['1', '5', '15'],
            start_date=start_date,
            end_date=end_date
        )
        
        # Display results
        print("\n📊 SRSI STRATEGY RESULTS:")
        print("=" * 50)
        
        if isinstance(results, dict):
            if 'trades' in results:
                trades = results['trades']
                print(f"Total Trades: {len(trades)}")
                
                if trades:
                    long_trades = [t for t in trades if t.get('signal') == 'BUY']
                    short_trades = [t for t in trades if t.get('signal') == 'SELL']
                    
                    print(f"Long Trades: {len(long_trades)}")
                    print(f"Short Trades: {len(short_trades)}")
                    
                    if long_trades:
                        avg_long_cost = sum(t['cost'] for t in long_trades) / len(long_trades)
                        print(f"Avg Long Trade Cost: ${avg_long_cost:.2f}")
                    
                    if short_trades:
                        avg_short_cost = sum(t['cost'] for t in short_trades) / len(short_trades)
                        print(f"Avg Short Trade Cost: ${avg_short_cost:.2f}")
            
            # Check for performance metrics
            if 'total_return' in results:
                print(f"\nPerformance Metrics:")
                print(f"Total Return: {results['total_return']:.2f}%")
                print(f"Sharpe Ratio: {results.get('sharpe_ratio', 'N/A')}")
                print(f"Max Drawdown: {results.get('max_drawdown', 'N/A')}%")
                print(f"Win Rate: {results.get('win_rate', 'N/A')}%")
        
        print(f"\n🎯 SRSI Multi-Timeframe Strategy Test Complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == '__main__':
    test_srsi_strategy()