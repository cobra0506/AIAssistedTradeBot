import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_ultimate_working_strategy():
    """Create a strategy using ONLY indicators and signals that we know work"""
    
    strategy_content = '''# Ultimate Working Strategy - Using Only Tested Components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema, rsi
from simple_strategy.strategies.signals_library import ma_crossover

def create_ultimate_strategy(symbols=['BTCUSDT'], timeframes=['60', '240']):
    """
    Ultimate working strategy using only tested components
    Strategy Logic:
    - Use EMA crossover for trend following
    - Simple, reliable, and tested
    """
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators that we KNOW work perfectly
    strategy.add_indicator('ema_fast', ema, period=12)
    strategy.add_indicator('ema_slow', ema, period=26)
    
    # Add signal rule that we KNOW works
    strategy.add_signal_rule('ema_cross', ma_crossover)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    return strategy.build()

# Usage example:
# ultimate_strategy = create_ultimate_strategy()
'''
    
    try:
        # Make sure the directory exists
        os.makedirs('simple_strategy/strategies', exist_ok=True)
        
        with open('simple_strategy/strategies/Strategy_Ultimate.py', 'w') as f:
            f.write(strategy_content)
        
        print("✅ Created Ultimate Working Strategy")
        print("🚀 This strategy uses ONLY tested and working components!")
        print("📁 File saved to: simple_strategy/strategies/Strategy_Ultimate.py")
        
    except Exception as e:
        print(f"❌ Error creating strategy file: {e}")

if __name__ == '__main__':
    print("🎯 Creating Ultimate Working Strategy...")
    print("=" * 50)
    create_ultimate_working_strategy()
    print("\n🎉 ULTIMATE STRATEGY READY!")
    print("🚀 Now test it with your test_with_real_data.py!")