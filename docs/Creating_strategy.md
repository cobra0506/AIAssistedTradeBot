Complete Guide: Creating a Strategy from Scratch for AIAssistedTradeBot 
Table of Contents 

     Understanding the Strategy Architecture 
     Strategy File Structure 
     Step-by-Step Strategy Creation 
     Working Examples 
     Common Pitfalls and Solutions 
     Testing and Debugging 
     

Understanding the Strategy Architecture 
How the System Works 

Your trading system uses a StrategyBuilder pattern with these key components: 

     StrategyBuilder: The main class that constructs strategies
     Indicators Library: Contains technical indicators (RSI, SMA, EMA, etc.)
     Signals Library: Contains signal generation functions (overbought_oversold, ma_crossover, etc.)
     Backtester Engine: Executes strategies and calculates performance metrics
     

Data Flow 

GUI → Strategy Registry → Strategy File → StrategyBuilder → Indicators → Signals → Backtester → Results

Strategy File Structure 

Every strategy file MUST follow this exact structure: 
python

"""
Strategy Description - Brief explanation of what this strategy does
Author: Your Name
Date: 2025
"""

import sys
import os

# Add parent directories to path (REQUIRED)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import required components (REQUIRED)
from strategies.strategy_builder import StrategyBuilder
from strategies.indicators_library import rsi, sma, ema  # Add indicators you need
from strategies.signals_library import overbought_oversold, ma_crossover  # Add signals you need

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create strategy function (REQUIRED)
    
    Args:
        symbols: List of trading symbols (from GUI)
        timeframes: List of timeframes (from GUI)
        **params: Strategy parameters (from GUI)
    
    Returns:
        Built strategy object
    """
    # Handle None values (REQUIRED)
    if symbols is None or len(symbols) == 0:
        symbols = ['SOLUSDT']  # Default symbol
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['5m']  # Default timeframe
    
    # Get parameters with defaults (REQUIRED)
    param1 = params.get('param1_name', default_value)
    param2 = params.get('param2_name', default_value)
    
    # Create strategy (REQUIRED)
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators (REQUIRED - at least one)
    strategy.add_indicator('indicator_name', indicator_function, param1=value1, param2=value2)
    
    # Add signal rules (REQUIRED - at least one)
    strategy.add_signal_rule('signal_name', signal_function, 
                           indicator='indicator_name', 
                           param1=value1, param2=value2)
    
    # Set signal combination (REQUIRED)
    strategy.set_signal_combination('majority_vote')  # Options: 'majority_vote', 'weighted', 'unanimous'
    
    # Set strategy info (REQUIRED)
    strategy.set_strategy_info('Strategy_Name', '1.0.0')
    
    return strategy.build()

# Define strategy parameters for GUI (REQUIRED)
STRATEGY_PARAMETERS = {
    'param1_name': {
        'type': 'int|float|str', 
        'default': default_value, 
        'min': min_value, 
        'max': max_value, 
        'description': 'Parameter description'
    },
    'param2_name': {
        'type': 'int|float|str', 
        'default': default_value, 
        'min': min_value, 
        'max': max_value, 
        'description': 'Parameter description'
    }
}

Step-by-Step Strategy Creation 
Step 1: Choose Your Strategy Logic 

Decide what type of strategy you want to create: 
Strategy Type
 	
Indicators
 	
Signals
 	
Description
 
 Mean Reversion	RSI, Stochastic	overbought_oversold	Buy when oversold, sell when overbought 
Trend Following	SMA, EMA	ma_crossover	Buy when fast MA crosses above slow MA 
Momentum	MACD, RSI	macd_signals	Buy when MACD crosses above signal line 
Volatility	Bollinger Bands	bollinger_bands_signals	Buy when price touches lower band 
 
  
Step 2: Create the File 

     Navigate to simple_strategy/strategies/
     Create a new file named Strategy_YourName.py (MUST start with "Strategy_")
     Use the template structure above
     

Step 3: Add Imports 
python

# Required imports
from strategies.strategy_builder import StrategyBuilder
from strategies.indicators_library import rsi, sma, ema, macd, bollinger_bands
from strategies.signals_library import overbought_oversold, ma_crossover, macd_signals, bollinger_bands_signals

Step 4: Implement the create_strategy Function 
Example 1: RSI Mean Reversion Strategy 
python

def create_strategy(symbols=None, timeframes=None, **params):
    """Create RSI Mean Reversion Strategy"""
    # Handle None values
    if symbols is None or len(symbols) == 0:
        symbols = ['SOLUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['5m']
    
    # Get parameters
    rsi_period = params.get('rsi_period', 14)
    oversold = params.get('oversold', 30)
    overbought = params.get('overbought', 70)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add RSI indicator
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    
    # Add signal rule
    strategy.add_signal_rule('rsi_signal', overbought_oversold,
                           indicator='rsi',
                           overbought=overbought,
                           oversold=oversold)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    # Set strategy info
    strategy.set_strategy_info('RSI_Mean_Reversion', '1.0.0')
    
    return strategy.build()

# GUI parameters
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 50, 'description': 'RSI calculation period'},
    'oversold': {'type': 'int', 'default': 30, 'min': 10, 'max': 50, 'description': 'Oversold threshold (BUY signal)'},
    'overbought': {'type': 'int', 'default': 70, 'min': 50, 'max': 90, 'description': 'Overbought threshold (SELL signal)'}
}

Example 2: Moving Average Crossover Strategy 
python

def create_strategy(symbols=None, timeframes=None, **params):
    """Create Moving Average Crossover Strategy"""
    # Handle None values
    if symbols is None or len(symbols) == 0:
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['1h']
    
    # Get parameters
    fast_period = params.get('fast_period', 10)
    slow_period = params.get('slow_period', 30)
    ma_type = params.get('ma_type', 'sma')
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add indicators based on type
    if ma_type == 'sma':
        strategy.add_indicator('fast_ma', sma, period=fast_period)
        strategy.add_indicator('slow_ma', sma, period=slow_period)
    else:  # ema
        strategy.add_indicator('fast_ma', ema, period=fast_period)
        strategy.add_indicator('slow_ma', ema, period=slow_period)
    
    # Add signal rule
    strategy.add_signal_rule('ma_crossover', ma_crossover,
                           fast_ma='fast_ma',
                           slow_ma='slow_ma')
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    # Set strategy info
    strategy.set_strategy_info('MA_Crossover', '1.0.0')
    
    return strategy.build()

# GUI parameters
STRATEGY_PARAMETERS = {
    'fast_period': {'type': 'int', 'default': 10, 'min': 1, 'max': 50, 'description': 'Fast moving average period'},
    'slow_period': {'type': 'int', 'default': 30, 'min': 10, 'max': 100, 'description': 'Slow moving average period'},
    'ma_type': {'type': 'str', 'default': 'sma', 'options': ['sma', 'ema'], 'description': 'Moving average type'}
}

Step 5: Add GUI Parameters 

The STRATEGY_PARAMETERS dictionary defines what appears in your GUI: 
python

STRATEGY_PARAMETERS = {
    'parameter_name': {
        'type': 'int|float|str',           # Data type
        'default': default_value,         # Default value
        'min': minimum_value,             # Minimum value (for int/float)
        'max': maximum_value,             # Maximum value (for int/float)
        'options': ['option1', 'option2'], # Options (for str type)
        'description': 'Description'      # Help text
    }
}

Working Examples 
Complete RSI Strategy (Copy-Paste Ready) 
python

"""
RSI Mean Reversion Strategy
Buys when RSI is oversold, sells when RSI is overbought
Author: AI Assisted TradeBot
Date: 2025
"""
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from strategies.strategy_builder import StrategyBuilder
from strategies.indicators_library import rsi
from strategies.signals_library import overbought_oversold

def create_strategy(symbols=None, timeframes=None, **params):
    """Create RSI Mean Reversion Strategy"""
    # Handle None values properly
    if symbols is None or len(symbols) == 0:
        symbols = ['SOLUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['5m']
    
    # Get parameters with defaults
    rsi_period = params.get('rsi_period', 14)
    oversold = params.get('oversold', 30)
    overbought = params.get('overbought', 70)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add RSI indicator
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    
    # Add signal rule
    strategy.add_signal_rule('rsi_signal', overbought_oversold,
                           indicator='rsi',
                           overbought=overbought,
                           oversold=oversold)
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    # Set strategy info
    strategy.set_strategy_info('RSI_Mean_Reversion', '1.0.0')
    
    return strategy.build()

# GUI parameters
STRATEGY_PARAMETERS = {
    'rsi_period': {'type': 'int', 'default': 14, 'min': 5, 'max': 50, 'description': 'RSI calculation period'},
    'oversold': {'type': 'int', 'default': 30, 'min': 10, 'max': 50, 'description': 'Oversold threshold (BUY signal)'},
    'overbought': {'type': 'int', 'default': 70, 'min': 50, 'max': 90, 'description': 'Overbought threshold (SELL signal)'}
}

Complete MACD Strategy (Copy-Paste Ready) 
python

"""
MACD Momentum Strategy
Buys when MACD crosses above signal line, sells when MACD crosses below signal line
Author: AI Assisted TradeBot
Date: 2025
"""
import sys
import os

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from strategies.strategy_builder import StrategyBuilder
from strategies.indicators_library import macd
from strategies.signals_library import macd_signals

def create_strategy(symbols=None, timeframes=None, **params):
    """Create MACD Momentum Strategy"""
    # Handle None values properly
    if symbols is None or len(symbols) == 0:
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['1h']
    
    # Get parameters with defaults
    fast_period = params.get('fast_period', 12)
    slow_period = params.get('slow_period', 26)
    signal_period = params.get('signal_period', 9)
    
    # Create strategy
    strategy = StrategyBuilder(symbols, timeframes)
    
    # Add MACD indicator
    strategy.add_indicator('macd', macd, 
                          fast_period=fast_period,
                          slow_period=slow_period,
                          signal_period=signal_period)
    
    # Add signal rule
    strategy.add_signal_rule('macd_signal', macd_signals,
                           macd_line='macd',
                           signal_line='signal')
    
    # Set signal combination
    strategy.set_signal_combination('majority_vote')
    
    # Set strategy info
    strategy.set_strategy_info('MACD_Momentum', '1.0.0')
    
    return strategy.build()

# GUI parameters
STRATEGY_PARAMETERS = {
    'fast_period': {'type': 'int', 'default': 12, 'min': 5, 'max': 20, 'description': 'MACD fast period'},
    'slow_period': {'type': 'int', 'default': 26, 'min': 15, 'max': 50, 'description': 'MACD slow period'},
    'signal_period': {'type': 'int', 'default': 9, 'min': 5, 'max': 20, 'description': 'MACD signal period'}
}
 
 
 
Common Pitfalls and Solutions 
Pitfall 1: Strategy Not Showing in GUI 

Problem: Strategy doesn't appear in the GUI dropdown
Solution:  

     File name MUST start with "Strategy_" (e.g., Strategy_MyStrategy.py)
     File MUST be in simple_strategy/strategies/ folder
     File MUST have create_strategy function and STRATEGY_PARAMETERS dictionary
     

Pitfall 2: Zero Trades Generated 

Problem: Strategy runs but generates zero trades
Solution: 

     Check if symbol data exists in data/ folder
     Ensure parameters are reasonable (not too aggressive/conservative)
     Add debug prints to see if signals are being generated
     

Pitfall 3: "NoneType" Object Errors 

Problem: Error about NoneType object not iterable
Solution: 

     Always handle None values in create_strategy function:
     

python

if symbols is None or len(symbols) == 0:
    symbols = ['SOLUSDT']
 
 
 
Pitfall 4: Signal Combination Method Invalid 

Problem: Error about invalid signal combination method
Solution: Use only valid methods: 'majority_vote', 'weighted', or 'unanimous' 
Pitfall 5: Insufficient Balance Errors 

Problem: Trades not executing due to insufficient balance
Solution: 

     Use cheaper assets (ADAUSDT, DOGEUSDT) for testing
     Adjust risk per trade percentage
     This is normal behavior, not an error
     

Testing and Debugging 
Step 1: Basic Validation 

     Create strategy file with correct structure
     Restart GUI
     Check if strategy appears in dropdown
     Try to create strategy instance
     

Step 2: Signal Generation Test 

Add debug prints to verify signal generation: 
python

def create_strategy(symbols=None, timeframes=None, **params):
    print(f"DEBUG: symbols={symbols}, timeframes={timeframes}")
    # ... rest of code
 
 
 
Step 3: Backtest Execution 

     Select strategy in GUI
     Choose appropriate symbol (cheaper assets for testing)
     Set reasonable date range
     Run backtest
     Check for trade execution in logs
     

Step 4: Performance Analysis 

Review results: 

     Total Trades > 0: Strategy is generating signals
     Win Rate > 0%: Some trades are profitable
     Sharpe Ratio > 0: Strategy has positive risk-adjusted returns
     Max Drawdown < 20%: Acceptable risk level
     

Quick Reference Checklist 

Before running your strategy, verify: 

     File name starts with "Strategy_"
     File is in simple_strategy/strategies/ folder
     All imports are correct
     create_strategy function exists
     STRATEGY_PARAMETERS dictionary exists
     None values are handled properly
     At least one indicator is added
     At least one signal rule is added
     Signal combination method is valid
     Strategy info is set
     Data files exist for chosen symbols
     

Conclusion 

Creating a working strategy for AIAssistedTradeBot is straightforward once you understand the required structure and common pitfalls. Follow this guide, and you'll be able to create strategies that work the first time, every time. 

Remember: The key to success is following the exact structure, handling edge cases properly, and testing with appropriate assets and parameters. 

Happy strategy creation! 🚀 