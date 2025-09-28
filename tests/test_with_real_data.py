import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import strategy functions
from simple_strategy.strategies.Strategy_1_Trend_Following import create_trend_following_strategy
from simple_strategy.strategies.Strategy_2_mean_reversion import create_mean_reversion_strategy
from simple_strategy.strategies.Strategy_3_Multi_Indicator import create_multi_indicator_strategy

# Import required components
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.shared.data_feeder import DataFeeder

def test_with_real_data():
    """Test strategies with real historical data"""
    print("🚀 Testing Strategies with Real Data")
    print("=" * 60)
    
    # Use your actual data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    print(f"📁 Using data directory: {data_dir}")
    
    # Check what files are available
    if os.path.exists(data_dir):
        files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        print(f"📊 Available data files: {files}")
    else:
        print("❌ Data directory does not exist")
        return
    
    # Calculate date range for last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    print(f"📅 Testing date range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Test each strategy with correct timeframes
    strategies = [
        ("Trend Following", create_trend_following_strategy, ['60', '240']),  # 1h, 4h
        ("Mean Reversion", create_mean_reversion_strategy, ['60', '120']),   # 1h, 2h
        ("Multi-Indicator", create_multi_indicator_strategy, ['60', '240'])  # 1h, 4h
    ]
    
    for strategy_name, strategy_func, timeframes in strategies:
        print(f"\n🎯 Testing {strategy_name} Strategy")
        print("-" * 40)
        print(f"📊 Using timeframes: {timeframes}")
        
        try:
            # Create strategy
            strategy = strategy_func()
            print(f"✅ Strategy created successfully")
            
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
            print(f"✅ BacktesterEngine created successfully")
            
            # Run backtest with correct timeframes and date range
            results = backtester.run_backtest(
                symbols=['BTCUSDT'],
                timeframes=timeframes,
                start_date=start_date,
                end_date=end_date
            )
            print(f"✅ Backtest completed")
            print(f"📊 Results: {results}")
            
            # If results contain performance metrics, display them
            if isinstance(results, dict) and 'total_return' in results:
                print(f"💰 Total Return: {results['total_return']:.2f}%")
                print(f"📈 Sharpe Ratio: {results.get('sharpe_ratio', 'N/A')}")
                print(f"📉 Max Drawdown: {results.get('max_drawdown', 'N/A')}")
                print(f"🎯 Win Rate: {results.get('win_rate', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error testing {strategy_name}: {e}")
            import traceback
            print(f"Full error: {traceback.format_exc()}")

if __name__ == '__main__':
    test_with_real_data()