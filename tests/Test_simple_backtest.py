# Test with minimal data
from simple_strategy.backtester.backtester_engine import BacktesterEngine
from simple_strategy.shared.data_feeder import DataFeeder

feeder = DataFeeder(data_dir='data')
backtest = BacktesterEngine(data_feeder=feeder, strategy=strategy)

# Test with just 1 day of data
results = backtest.run_backtest(
    symbols=['BTCUSDT'],
    timeframes=['1m'],
    start_date='2025-10-12',
    end_date='2025-10-13'
)

print(f"Results: {results['performance_metrics']}")