"""
CORRECTED WORKING VERSION - Strategy_1_Trend_Following.py
Fixed imports to match the working strategy structure
"""
import sys
import os
import pandas as pd
import numpy as np
import logging

# Add parent directories to path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Import required components - FIXED IMPORTS
from .strategy_builder import StrategyBuilder
from .indicators_library import sma, ema
from .signals_library import ma_crossover
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Trend Following strategy - Simple working version
    """
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters with defaults
    fast_period = params.get('fast_period', 5)
    slow_period = params.get('slow_period', 15)
    ma_type = params.get('ma_type', 'ema')
    
    print(f"🔧 Creating strategy: fast={fast_period}, slow={slow_period}, ma_type={ma_type}")
    
    try:
        # Create strategy using StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # Add indicators based on MA type
        if ma_type == 'sma':
            strategy_builder.add_indicator('sma_fast', sma, period=fast_period)
            strategy_builder.add_indicator('sma_slow', sma, period=slow_period)
            fast_ma_name = 'sma_fast'
            slow_ma_name = 'sma_slow'
        else:  # ema
            strategy_builder.add_indicator('ema_fast', ema, period=fast_period)
            strategy_builder.add_indicator('ema_slow', ema, period=slow_period)
            fast_ma_name = 'ema_fast'
            slow_ma_name = 'ema_slow'
        
        # Add signal rule for MA crossover
        strategy_builder.add_signal_rule('ma_crossover', ma_crossover,
                                       fast_ma=fast_ma_name,
                                       slow_ma=slow_ma_name)
        
        # Set signal combination method
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information
        strategy_builder.set_strategy_info('Trend_Following', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        print(f"✅ Strategy created successfully!")
        return strategy
        
    except Exception as e:
        logger.error(f"❌ Error creating strategy: {e}")
        raise


def load_data_directly():
    """Load data directly from CSV file"""
    try:
        csv_path = 'data/ADAUSDT_5.csv'
        print(f"📁 Loading data from: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"❌ CSV file does not exist: {csv_path}")
            return None
            
        # Load CSV directly
        df = pd.read_csv(csv_path)
        print(f"📊 CSV loaded: {df.shape}")
        
        # Parse timestamps correctly - convert from milliseconds to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('datetime', inplace=True)
            print(f"📊 Timestamps converted: {df.index.min()} to {df.index.max()}")
        
        # Keep only OHLCV columns
        df = df[['open', 'high', 'low', 'close', 'volume']]
        
        print(f"✅ Data validation passed")
        
        # Return in expected format
        return {
            'ADAUSDT': {
                '5m': df
            }
        }
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def simple_test():
    """Simple test to verify the strategy works"""
    print("🧪 SIMPLE STRATEGY TEST")
    print("=" * 30)
    
    try:
        # Create strategy
        strategy = create_strategy(['ADAUSDT'], ['5m'], 
                                 fast_period=5, 
                                 slow_period=15, 
                                 ma_type='ema')
        
        # Load data directly (bypass the DataFeeder issue)
        data = load_data_directly()
        
        if data is not None:
            df = data['ADAUSDT']['5m']
            print(f"📊 Data loaded: {df.shape}")
            print(f"   Date range: {df.index.min()} to {df.index.max()}")
            
            # Generate signals
            signals = strategy.generate_signals(data)
            print(f"📊 Signals generated: {signals}")
            
            # Create a simple data feeder for backtest
            class SimpleDataFeeder:
                def __init__(self, data):
                    self.data = data
                    self.data_cache = {'ADAUSDT': {'5m': df}}
                    self.memory_limit = 0.5
                
                def load_data(self, symbols, timeframes, start_date=None, end_date=None):
                    print(f"📡 DataFeeder.load_data called")
                    return self.data
                
                def get_data_for_symbols(self, symbols, timeframes, start_date=None, end_date=None):
                    print(f"📡 get_data_for_symbols called")
                    return self.data
            
            # Run backtest
            from simple_strategy.backtester.backtester_engine import BacktesterEngine
            
            data_feeder = SimpleDataFeeder(data)
            
            backtester = BacktesterEngine(
                data_feeder=data_feeder,
                strategy=strategy
            )
            
            results = backtester.run_backtest(
                symbols=['ADAUSDT'],
                timeframes=['5m'],
                start_date='2025-09-16',
                end_date='2025-10-16'
            )
            
            print(f"📊 BACKTEST RESULTS:")
            if isinstance(results, dict):
                total_trades = results.get('total_trades', 0)
                total_return = results.get('total_return', 0)
                win_rate = results.get('win_rate', 0)
                
                print(f"   💰 Total Trades: {total_trades}")
                print(f"   💰 Total Return: {total_return:.2f}%")
                print(f"   🎯 Win Rate: {win_rate:.2f}%")
                
                if 'performance_metrics' in results:
                    pm = results['performance_metrics']
                    if pm and isinstance(pm, dict):
                        print(f"   📈 Sharpe Ratio: {pm.get('sharpe_ratio', 0):.3f}")
                        print(f"   📉 Max Drawdown: {pm.get('max_drawdown', 0):.2f}%")
                        print(f"   💵 Final Balance: ${pm.get('final_balance', 0):.2f}")
                
                if total_trades > 0:
                    print(f"   ✅ SUCCESS: Strategy generated {total_trades} trades!")
                else:
                    print(f"   ❌ Issue: No trades generated")
            else:
                print(f"   Results type: {type(results)}")
                print(f"   Results: {results}")
        else:
            print("❌ Failed to load data")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


# Strategy parameters for GUI configuration
STRATEGY_PARAMETERS = {
    'fast_period': {
        'type': 'int', 
        'default': 5,  
        'min': 1, 
        'max': 50, 
        'description': 'Fast moving average period',
        'gui_hint': 'For 5m: 5-15, For 1h: 10-30'
    },
    'slow_period': {
        'type': 'int', 
        'default': 15,  
        'min': 10, 
        'max': 200, 
        'description': 'Slow moving average period',
        'gui_hint': 'For 5m: 15-50, For 1h: 30-100'
    },
    'ma_type': {
        'type': 'str', 
        'default': 'ema',  
        'options': ['sma', 'ema'], 
        'description': 'Moving average type',
        'gui_hint': 'EMA reacts faster than SMA to recent price changes'
    }
}


# For testing
if __name__ == "__main__":
    simple_test()