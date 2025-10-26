📚 COMPLETE GUIDE: Creating Strategies That Work First Time 🎯
🚫 COMMON MISTAKES TO AVOID (LEARNED FROM EXPERIENCE)
-----------------------------------------------------

### **1. GUI Parameter Issues**
* **Problem**: Strategy has many parameters but GUI can't show them all
* **Fix**: Use scrollable parameters (already implemented in GUI)
* **Solution**: No limit to parameters - GUI handles scrolling automatically

### **2. Signal Combination Method Errors**
* **Problem**: Using wrong signal combination method names
* **Wrong**: `'weighted_vote'`
* **Correct**: `'weighted'`
* **Valid Methods**: `['majority_vote', 'weighted', 'unanimous']`
* **Critical**: `'weighted'` requires weights parameter, `'unanimous'` requires ALL signals to agree

### **3. MACD Signal Reference Errors**
* **Problem**: Wrong MACD component references
* **Wrong**: `macd_line='macd_line', signal_line='signal_line'`
* **Correct**: `macd_line='macd', signal_line='macd'`
* **Reason**: MACD indicator creates components, but signal rules reference the main indicator name

### **4. Import Errors**
* **Problem**: Wrong class names in imports
* **Wrong**: `from backtester.backtester_engine import BacktestEngine`
* **Correct**: `from simple_strategy.backtester.backtester_engine import BacktesterEngine`
* **Reason**: Correct class name is `BacktesterEngine` (lowercase 't'), not `BacktestEngine`

### **5. Backtester Constructor Issues**
* **Problem**: Wrong constructor parameters
* **Wrong**: Direct parameter passing to BacktesterEngine
* **Correct**: Use DataFeeder first, then pass to BacktesterEngine
* **Pattern**: 
  ```python
  data_feeder = DataFeeder(data_dir, symbols, timeframes, start_date, end_date)
  backtester = BacktesterEngine(data_feeder=data_feeder, strategy=strategy)

6. CRITICAL: Missing Indicator Imports 🆕 

     Problem: Forgetting to import indicators used in strategy
     Error: NameError: name 'volume_sma' is not defined
     Solution: Always import all indicators you use:
    python

    from simple_strategy.strategies.indicators_library import ema, rsi, atr, volume_sma, bollinger_bands

7. Bollinger Bands Component Errors 🆕 

     Problem: Wrong usage of Bollinger Bands component parameter
     Wrong: bollinger_bands(period=20, std_dev=2, component='upper')
     Correct: Add the main indicator, it returns all components:
    python

    strategy_builder.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
    # Use: bb_data[0] = upper, bb_data[1] = middle, bb_data[2] = lower

8. StrategyBuilder Signal Rule Requirements 🆕 

     Problem: "No signal rules defined. Add at least one signal rule."
     Solution: StrategyBuilder requires at least one signal rule to work:
    python

    # ALWAYS add at least one signal rule
    strategy_builder.add_signal_rule('signal_name', signal_function, ...)

9. Multi-Timeframe Logic Errors 🆕 

     Problem: Complex multi-timeframe requirements that don't work
     Wrong: Requiring 1m AND 5m simultaneously without proper data handling
     Correct: 
    python

    # Check if timeframe exists in data before using it
    if '5m' in all_data.get(symbol, {}):
        trend_data = all_data[symbol]['5m']

10. Too Strict Entry Conditions 🆕 

     Problem: Multiple confirmations filtering out ALL signals
     Wrong: Requiring RSI + BB + Volume + Trend ALL to agree
     Solution: Start simple, add filters gradually:
    python

    # Start with 2 indicators max
    # Use 'majority_vote' instead of 'unanimous'
    # Add volume filters only if needed

11. Volume Requirements Too High 🆕 

     Problem: Volume multipliers of 110-200% are rarely met
     Wrong: current_volume > volume_sma * 2.0
     Better: current_volume > volume_sma * 1.1 (110%)
     Best: Start without volume filter, add if needed
     

12. Class Name Syntax Errors 🆕 

     Problem: Typos in class names causing syntax errors
     Wrong: class SimpleEMA RSIStrategy: (space in name)
     Correct: class SimpleEMARSIStrategy: (no spaces)
     Solution: Use consistent naming: CamelCase without spaces
     

13. Position Management Complexity 🆕 

     Problem: Complex position tracking that isn't properly implemented
     Wrong: self.positions[symbol] without proper cleanup
     Solution: Keep it simple or implement full lifecycle:
    python

    # Add position when entering
    self.positions[symbol] = {'type': 'LONG', 'entry_price': price}

    # Remove position when exiting
    if exit_condition:
        del self.positions[symbol]
        return 'SELL'

14. Indicator Reference Issues 🆕 

     Problem: Wrong way to reference indicator components
     Wrong: Using component names that don't exist
     Correct: Check what the indicator actually returns:
    python

    # Test what the indicator returns
    bb_data = df['bb'].iloc[-1]
    if isinstance(bb_data, (tuple, list)):
        upper, middle, lower = bb_data[0], bb_data[1], bb_data[2]

15. Zero Trades Problem 🆕 

     Problem: Strategy generates no trades at all
     Common Causes:
         Entry conditions too strict
         Multi-timeframe requirements not met
         Volume filters too aggressive
         Signal combination too restrictive ('unanimous')
         
     Solution: Start ultra-simple, add complexity gradually
     

🎯 START SIMPLE PRINCIPLE 

ALWAYS start with a simple working strategy, then add complexity: 
Phase 1: Ultra-Simple (Must Work) 
python

# Maximum 2 indicators
# No volume filters
# No multi-timeframe
# 'majority_vote' combination
# Fixed position size
 
 
 
Phase 2: Add One Enhancement 
python

# Add volume filter OR
# Add trend filter OR
# Add multi-timeframe OR
# Improve position sizing
 
 
 
Phase 3: Advanced Features 
python

# Add multiple confirmations
# Complex position management
# Advanced risk management

🛠️ WORKING RECIPE BOOK (Updated) 
Recipe 1: Ultra-Simple RSI (Guaranteed to Work) 
python

# Ingredients:
# - 1 RSI indicator
# - 1 overbought_oversold signal
# - No volume filter
# - No trend filter
# - Single timeframe

strategy_builder.add_indicator('rsi', rsi, period=14)
strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                               indicator='rsi', overbought=70, oversold=30)
strategy_builder.set_signal_combination('majority_vote')
 
 
 
Recipe 2: Simple EMA Crossover (Most Reliable) 
python

# Ingredients:
# - 2 EMAs
# - 1 ma_crossover signal
# - Conservative parameters
# - Single timeframe

strategy_builder.add_indicator('ema_fast', ema, period=10)
strategy_builder.add_indicator('ema_slow', ema, period=30)
strategy_builder.add_signal_rule('ema_cross', ma_crossover,
                               fast_ma='ema_fast', slow_ma='ema_slow')
strategy_builder.set_signal_combination('majority_vote')
 
 
 
Recipe 3: Simple Multi-Timeframe (Actually Works) 
python

# Ingredients:
# - 1m timeframe for entries
# - 5m timeframe for trend
# - Simple trend check
# - Proper data validation

# For 1m
strategy_builder.add_indicator('ema_fast_1m', ema, period=9)
strategy_builder.add_indicator('ema_slow_1m', ema, period=21)

# For 5m
strategy_builder.add_indicator('ema_trend_5m', ema, period=50)

# In signal generation:
if '5m' in all_data.get(symbol, {}):
    trend_ema = all_data[symbol]['5m']['ema_trend_5m'].iloc[-1]
    current_price = all_data[symbol]['5m']['close'].iloc[-1]
    bullish_trend = current_price > trend_ema
 
 
 
🚫 CRITICAL ERROR CHECKLIST 

Before running your strategy, check: 

     Imports: All indicators imported?
     Signal Rules: At least one signal rule added?
     Class Names: No spaces or special characters?
     Bollinger Bands: Using main indicator, not components?
     Multi-timeframe: Proper data validation?
     Volume Filters: Not too aggressive (start < 1.2x)?
     Signal Combination: 'majority_vote' for testing?
     Position Management: Simple or fully implemented?
     

🎯 DEBUGGING ZERO TRADES 

If your strategy generates zero trades: 

     Check entry conditions: Are they too strict?
     Check volume requirements: Lower to 1.1x or remove entirely
     Check signal combination: Use 'majority_vote' instead of 'unanimous'
     Check multi-timeframe: Remove and test single timeframe first
     Check data availability: Ensure you have the required timeframe data
     Add debug logging: Print signal conditions to see why no trades
     

📊 PERFORMANCE EXPECTATIONS 

Realistic expectations for simple strategies: 

     Win Rate: 45-65% is normal
     Total Return: -1% to +1% per week is realistic
     Trade Frequency: 1-20 trades per week depending on strategy
     Sharpe Ratio: Anything above 1.0 is good, above 2.0 is excellent
     

⚠️ WARNING SIGNS 

Your strategy is too complex if: 

     It generates zero trades
     It has more than 3 indicators
     It requires more than 2 confirmations
     It uses 'unanimous' signal combination
     It has volume multipliers above 1.5x
     It requires multiple timeframes without proper validation
     

🎯 FILE STRUCTURE (NON-NEGOTIABLE) 

Step 1: File Naming
✅ CORRECT: Strategy_MyStrategy.py
❌ WRONG: MyStrategy.py, strategy_MyStrategy.py, My_Strategy.py 

Step 2: File Location
📁 simple_strategy/strategies/Strategy_MyStrategy.py 

Step 3: Required Elements 

     STRATEGY_PARAMETERS dictionary at TOP
     create_strategy() function
     simple_test() function
     Proper imports
     Error handling
     

📝 TEMPLATE STRUCTURE (Copy-Paste This)
"""
Your Strategy Description """ 

import sys
import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional 
Add parent directories to path for proper imports 

current_dir = os.path.dirname(os.path.abspath(file))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 
Import required components 

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import ema, rsi  # Add ALL indicators you use
from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold  # Add ALL signals you use
from simple_strategy.shared.strategy_base import StrategyBase 
Configure logging 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name) 
CRITICAL: STRATEGY_PARAMETERS (AT TOP) 

STRATEGY_PARAMETERS = {
    'parameter_name': {
        'type': 'int',  # 'int', 'float', 'str'
        'default': 14,
        'min': 5,
        'max': 50,
        'description': 'Parameter description',
        'gui_hint': 'GUI hint text'
    }
} 

def create_strategy(symbols=None, timeframes=None, **params):
    """CREATE STRATEGY FUNCTION - Required by GUI"""
    # Handle None/empty values
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['5m'] 
try:
    strategy_builder = StrategyBuilder(symbols, timeframes)
    
    # Add indicators
    for timeframe in timeframes:
        strategy_builder.add_indicator(f'indicator_{timeframe}', indicator_function, period=parameter)
    
    # Add signal rules (AT LEAST ONE)
    entry_timeframe = timeframes[0]
    strategy_builder.add_signal_rule('signal_name', signal_function, ...)
    
    # Set signal combination
    strategy_builder.set_signal_combination('majority_vote')  # Start with majority_vote
    
    strategy_builder.set_strategy_info('Strategy_Name', '1.0.0')
    strategy = strategy_builder.build()
    
    return strategy
    
except Exception as e:
    logger.error(f"❌ Error creating strategy: {e}")
    raise

class YourStrategyClass(StrategyBase):
    """Your Strategy Class""" 
def __init__(self, symbols, timeframes, config):
    super().__init__(name="Your_Strategy_Name", symbols=symbols, timeframes=timeframes, config=config)
    # Your parameters
    self.parameter = config.get('parameter_name', default_value)
    
def calculate_position_size(self, symbol, current_price=None, signal_strength=1.0):
    return 0.001  # Simple fixed size for testing

def generate_signals(self, data):
    signals = {}
    for symbol in data:
        signals[symbol] = {}
        for timeframe in data[symbol]:
            signals[symbol][timeframe] = self._generate_single_signal(data[symbol][timeframe], symbol, timeframe)
    return signals

def _generate_single_signal(self, df, symbol, timeframe):
    try:
        # Your signal logic here
        # Keep it simple to start
        return 'HOLD'
    except Exception as e:
        logger.error(f"Error: {e}")
        return 'HOLD'

def create_your_strategy_instance(symbols=None, timeframes=None, **params):
    """Optional but recommended"""
    try:
        strategy = YourStrategyClass(symbols, timeframes, params)
        return strategy
    except Exception as e:
        logger.error(f"Error: {e}")
        raise 

def simple_test():
    """Simple test - MUST EXIST"""
    try:
        strategy = create_strategy(symbols=['BTCUSDT'], timeframes=['5m'])
        print(f"✅ Strategy created successfully: {strategy.name}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False 

if name == "main":
    simple_test()
''' 

Remember: **Start simple, ensure it works, then add complexity gradually!**
