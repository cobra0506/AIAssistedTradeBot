import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi, sma
from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.shared.data_feeder import DataFeeder

def main():
    print("🚀 Testing Optimized Strategy")
    print("=" * 50)
    
    # Create strategy with the BEST parameters we found
    print("📊 Creating strategy with optimized parameters...")
    strategy = StrategyBuilder(['BTCUSDT'], ['60'])
    
    # Add indicators with OPTIMIZED settings
    strategy.add_indicator('rsi', rsi, period=9)  # Best RSI period: 9
    strategy.add_indicator('sma_short', sma, period=14)  # Best short SMA: 14
    strategy.add_indicator('sma_long', sma, period=40)  # Best long SMA: 40
    
    # Add signals with OPTIMIZED settings
    strategy.add_signal_rule('rsi_signal', overbought_oversold,
                            indicator='rsi',
                            oversold=21.16,    # Best oversold level
                            overbought=77.32)  # Best overbought level
    
    strategy.add_signal_rule('sma_crossover', ma_crossover,
                            fast_ma='sma_short',
                            slow_ma='sma_long')
    
    optimized_strategy = strategy.build()
    
    # Backtest the optimized strategy
    print("🔍 Backtesting optimized strategy...")
    data_feeder = DataFeeder(data_dir='data')
    backtester = BacktesterEngine(data_feeder=data_feeder, strategy=optimized_strategy)
    
    results = backtester.run_backtest(
        symbols=['BTCUSDT'],
        timeframes=['60'],
        start_date='2025-09-23',
        end_date='2025-10-21'
    )
    
    # Show results
    performance = results.get('performance_metrics', {})
    print("\n🎉 OPTIMIZED STRATEGY RESULTS:")
    print("=" * 50)
    print(f"💰 Total Return: {performance.get('total_return', 0):.2%}")
    print(f"🎯 Win Rate: {performance.get('win_rate', 0):.2%}")
    print(f"📈 Sharpe Ratio: {performance.get('sharpe_ratio', 0):.2f}")
    print(f"📉 Max Drawdown: {performance.get('max_drawdown', 0):.2%}")
    print(f"🔄 Total Trades: {performance.get('total_trades', 0)}")
    
    print("\n✅ You're now using the strategy with the best settings!")

if __name__ == "__main__":
    main()