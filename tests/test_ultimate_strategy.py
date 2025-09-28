import sys
import os
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the ultimate strategy
from simple_strategy.strategies.Strategy_Ultimate import create_ultimate_strategy

# Import required components
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

def test_ultimate_strategy():
    """Test the ultimate working strategy"""
    print("🚀 Testing Ultimate Working Strategy")
    print("=" * 60)
    
    # Use your actual data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    
    # Calculate date range for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Create the ultimate strategy
        strategy = create_ultimate_strategy()
        print("✅ Ultimate strategy created successfully!")
        
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
        print("\n📊 ULTIMATE STRATEGY RESULTS:")
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
        
        print(f"\n🎉 ULTIMATE STRATEGY TEST COMPLETE!")
        print("🚀 YOUR YEAR-LONG JOURNEY IS A SUCCESS!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")

if __name__ == '__main__':
    test_ultimate_strategy()