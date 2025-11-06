import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from simple_strategy.optimization import BayesianOptimizer, ParameterSpace
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.shared.data_feeder import DataFeeder

def main():
    print("🚀 Starting Strategy Optimization Example")
    
    # Initialize data feeder
    print("📊 Initializing DataFeeder...")
    data_feeder = DataFeeder(data_dir='data')
    
    # Create parameter space
    print("🔧 Setting up parameter space...")
    param_space = ParameterSpace()
    
    # RSI parameters
    param_space.add_int('rsi_period', 5, 30, step=1)
    param_space.add_float('rsi_oversold', 20, 40)
    param_space.add_float('rsi_overbought', 60, 80)
    
    # Moving average parameters
    param_space.add_int('sma_short_period', 5, 20, step=1)
    param_space.add_int('sma_long_period', 20, 50, step=5)
    
    print(f"📋 Parameter space created with {len(param_space.get_parameters())} parameters")
    
    # Create optimizer
    print("🎯 Initializing Bayesian optimizer...")
    optimizer = BayesianOptimizer(
        data_feeder=data_feeder,
        study_name='example_strategy_optimization',
        direction='maximize',
        n_trials=10,  # Start with small number for testing
        timeout=600    # 10 minutes timeout
    )
    
    # Run optimization with dates that match your actual data
    print("🚀 Starting optimization...")
    best_params, best_score = optimizer.optimize(
        strategy_builder_class=StrategyBuilder,
        parameter_space=param_space,
        symbols=['BTCUSDT'],
        timeframes=['60'],  # Matches your BTCUSDT_60.csv file
        start_date='2025-09-23',  # Start after your data begins
        end_date='2025-10-21',    # End before your data ends
        metric='sharpe_ratio'
    )
    
    print(f"\n🎉 Optimization Complete!")
    print(f"📈 Best Sharpe ratio: {best_score:.4f}")
    print(f"⚙️ Best parameters:")
    for param, value in best_params.items():
        print(f"   {param}: {value}")
    
    # Get optimization history
    history = optimizer.get_optimization_history()
    print(f"\n📊 Optimization completed: {len(history)} trials")
    
    # Save results
    if not history.empty:
        history.to_csv('optimization_results.csv', index=False)
        print("💾 Results saved to optimization_results.csv")

if __name__ == "__main__":
    main()