📚 COMPLETE GUIDE: Creating Strategies That Work First Time 
🎯 File Structure (NON-NEGOTIABLE) 
Step 1: File Naming 

✅ CORRECT: Strategy_mystategy.py
❌ WRONG: mystategy.py, MyStrategy.py, strategy_mystategy.py

Step 2: File Location 

📁 simple_strategy/strategies/Strategy_mystategy.py

📝 Template Structure (Copy-Paste This) 
python
 
"""
Your Strategy Description
"""

import sys
import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional

# Add parent directories to path for proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import required components
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import sma, ema, rsi  # Add indicators you need
from simple_strategy.strategies.signals_library import ma_crossover, threshold_crossing  # Add signals you need
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STRATEGY_PARAMETERS (GUI Configuration)
---------------------------------------
This dictionary defines what parameters appear in the GUI for users to configure.
Place this at the TOP after imports for better code organization.

def create_strategy(symbols=None, timeframes=None, **params):
    """
    Create Your Strategy - BASIC VERSION
    This function MUST exist and work with StrategyBuilder
    """
    # DEBUG: Log what we're getting
    logger.info(f"🔧 DEBUG: create_strategy called with:")
    logger.info(f" - symbols: {symbols}")
    logger.info(f" - timeframes: {timeframes}")
    logger.info(f" - params: {params}")
    
    # CRITICAL: Handle None/empty values
    if symbols is None or len(symbols) == 0:
        logger.warning(f"🔧 DEBUG: symbols is None or empty, using ['BTCUSDT']")
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        logger.warning(f"🔧 DEBUG: timeframes is None or empty, using ['5m']")
        timeframes = ['5m']
    
    try:
        # Create strategy using StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # Add indicators (use existing ones from indicators_library)
        strategy_builder.add_indicator('sma_fast', sma, period=12)
        strategy_builder.add_indicator('sma_slow', sma, period=26)
        
        # Add signal rules (use existing ones from signals_library)
        strategy_builder.add_signal_rule('ma_crossover', ma_crossover,
                                       fast_ma='sma_fast',
                                       slow_ma='sma_slow')
        
        # Set signal combination method
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information
        strategy_builder.set_strategy_info('Your_Strategy_Name', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        logger.info(f"✅ STRATEGY CREATED SUCCESSFULLY!")
        logger.info(f" - Strategy Name: {strategy.name}")
        logger.info(f" - Strategy Symbols: {strategy.symbols}")
        logger.info(f" - Strategy Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"❌ ERROR CREATING STRATEGY: {e}")
        import traceback
        traceback.print_exc()
        raise

class YourStrategyStrategy(StrategyBase):
    """
    Your Strategy Class - REAL LOGIC GOES HERE
    """
    
    def __init__(self, symbols: List[str], timeframes: List[str], config: Dict[str, Any]):
        """
        Initialize your strategy
        """
        # CRITICAL: Initialize with EXACT symbols and timeframes provided
        super().__init__(
            name="Your_Strategy_Name",
            symbols=symbols,
            timeframes=timeframes,
            config=config
        )
        
        # Strategy-specific parameters
        self.your_param1 = config.get('your_param1', 20)
        self.your_param2 = config.get('your_param2', 80)
        
        # Risk management
        self.max_risk_per_trade = config.get('max_risk_per_trade', 0.002)
        self.min_position_size = 0.01
        self.max_position_size = 100.0
        
        # Validate parameters
        self._validate_parameters()
        
        logger.info(f"📈 YourStrategyStrategy initialized:")
        logger.info(f"   - Symbols: {self.symbols}")
        logger.info(f"   - Timeframes: {self.timeframes}")
        logger.info(f"   - Your Param1: {self.your_param1}")
        logger.info(f"   - Your Param2: {self.your_param2}")
    
    def _validate_parameters(self):
        """Validate strategy parameters"""
        # Add your validation logic here
        pass
    
    def calculate_position_size(self, symbol: str, current_price: float = None, signal_strength: float = 1.0) -> float:
        """
        Calculate position size - MUST EXIST
        """
        try:
            # Calculate position value based on risk management
            position_value = self.balance * self.max_risk_per_trade * signal_strength
            
            # Calculate position size
            if current_price and current_price > 0:
                position_size = position_value / current_price
            else:
                position_size = self.min_position_size
            
            # Apply position size limits
            position_size = max(self.min_position_size, min(position_size, self.max_position_size))
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return self.min_position_size
    
    def generate_signals(self, data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Dict[str, str]]:
        """
        Generate trading signals - MUST EXIST
        """
        signals = {}
        
        try:
            for symbol in data:
                signals[symbol] = {}
                
                for timeframe in data[symbol]:
                    # Generate signal for each timeframe
                    signal = self._generate_single_signal(data[symbol][timeframe], symbol, timeframe)
                    signals[symbol][timeframe] = signal
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
        
        return signals
    
    def _generate_single_signal(self, df: pd.DataFrame, symbol: str, timeframe: str) -> str:
        """
        Generate a single trading signal - MUST EXIST
        Put your actual strategy logic here
        """
        try:
            if len(df) < 20:  # Need enough data
                return 'HOLD'
            
            # YOUR STRATEGY LOGIC GOES HERE
            # Example: Simple RSI strategy
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = rsi.iloc[-1]
            
            # Simple logic
            if current_rsi < 30:
                return 'BUY'
            elif current_rsi > 70:
                return 'SELL'
            else:
                return 'HOLD'
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol} {timeframe}: {e}")
            return 'HOLD'

def create_your_strategy_instance(symbols=None, timeframes=None, **params):
    """
    Create your strategy instance - OPTIONAL but recommended
    """
    try:
        if symbols is None:
            symbols = ['BTCUSDT']
        if timeframes is None:
            timeframes = ['5m']
        
        strategy = YourStrategyStrategy(symbols, timeframes, params)
        
        logger.info(f"✅ Your Strategy created successfully")
        return strategy
        
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise

# NOTE: You only need ONE STRATEGY_PARAMETERS dictionary at the TOP of the file
# The GUI will automatically detect and use these parameters

def simple_test():
    """Simple test to verify the strategy works - MUST EXIST"""
    try:
        # Test strategy creation
        strategy = create_strategy(
            symbols=['BTCUSDT'],
            timeframes=['5m'],
            your_param1=20,
            your_param2=80
        )
        
        print(f"✅ Strategy created successfully: {strategy.name}")
        print(f"   - Symbols: {strategy.symbols}")
        print(f"   - Timeframes: {strategy.timeframes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing strategy: {e}")
        return False

# For testing - MUST EXIST
if __name__ == "__main__":
    simple_test()
 
 
 
🎯 Critical Requirements Checklist 
✅ MUST HAVE (GUI Detection): 

     File Name: Strategy_*.py
     STRATEGY_PARAMETERS: At TOP (defines GUI parameters)
     create_strategy() function: Must exist and work with StrategyBuilder
     simple_test() function: Must exist
     if name == "main": Must exist 

     ⚠️ OPTIONAL (Advanced Strategies):
     Strategy Class: Only needed for custom logic beyond StrategyBuilder 
     

✅ MUST HAVE (Strategy Functionality): 

     init() method: Proper initialization with super().init()
     calculate_position_size() method: Must exist
     generate_signals() method: Must exist
     _generate_single_signal() method: Must exist
     _validate_parameters() method: Must exist
     

✅ MUST HANDLE (Error Prevention): 

     None/empty symbols: Use default ['BTCUSDT']
     None/empty timeframes: Use default ['5m']
     Import errors: Use try/except blocks
     Missing data: Check DataFrame length before processing
     

🚨 Common Mistakes to Avoid 
❌ File Structure Mistakes: python

WRONG - Missing STRATEGY_PARAMETERS
-----------------------------------
def create_strategy(): pass
WRONG - STRATEGY_PARAMETERS in wrong place
-------------------------------------------
class Strategy: pass
def simple_test(): pass
STRATEGY_PARAMETERS = {}  # Should be at TOP!

RIGHT - Correct structure:
---------------------------
STRATEGY_PARAMETERS = {}  # At TOP after imports
def create_strategy(): pass
class Strategy: pass  # Optional
def simple_test(): pass

❌ Import Mistakes: 
python

# WRONG - Don't import indicators that don't exist
from simple_strategy.strategies.indicators_library import stochastic_rsi  # May not exist

# RIGHT - Use existing indicators
from simple_strategy.strategies.indicators_library import sma, ema, rsi
 
 
❌ Method Signature Mistakes: 
python

# WRONG - Missing required parameters
def calculate_position_size(self):
    pass

# RIGHT - Full signature
def calculate_position_size(self, symbol: str, current_price: float = None, signal_strength: float = 1.0) -> float:
    pass
 
 
🎯 Quick Start Template 

Just copy the template above and replace: 

     YourStrategyStrategy → Your strategy name
     Your_Strategy_Name → Your strategy display name
     your_param1/your_param2 → Your actual parameters
     Logic in _generate_single_signal() → Your actual strategy logic
     

📊 Testing Your Strategy 

After creating the file: 

     Restart your GUI
     Check if strategy appears in dropdown
     Test with simple parameters
     Run backtest
     Check debug output for errors
     

This guide will ensure your strategy is detected and works on the FIRST TRY! 🎉 