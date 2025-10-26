📚 COMPLETE GUIDE: Creating Strategies That Work First Time 🎯

## 🚫 COMMON MISTAKES TO AVOID (LEARNED FROM EXPERIENCE)

### **1. GUI Parameter Issues**
- **Problem**: Strategy has many parameters but GUI can't show them all
- **Fix**: Use scrollable parameters (already implemented in GUI)
- **Solution**: No limit to parameters - GUI handles scrolling automatically

### **2. Signal Combination Method Errors**
- **Problem**: Using wrong signal combination method names
- **Wrong**: `'weighted_vote'`  
- **Correct**: `'weighted'`
- **Valid Methods**: `['majority_vote', 'weighted', 'unanimous']`

### **3. MACD Signal Reference Errors**
- **Problem**: Wrong MACD component references
- **Wrong**: `macd_line='macd_line', signal_line='signal_line'`
- **Correct**: `macd_line='macd', signal_line='macd'`
- **Reason**: MACD indicator creates components, but signal rules reference the main indicator name

### **4. Import Errors**
- **Problem**: Wrong class names in imports
- **Wrong**: `from backtester.backtester_engine import BacktestEngine`
- **Correct**: `from simple_strategy.backtester.backtester_engine import BacktesterEngine`
- **Reason**: Correct class name is `BacktesterEngine` (lowercase 't'), not `BacktestEngine`

### **5. Backtester Constructor Issues**
- **Problem**: Wrong constructor parameters
- **Wrong**: Direct parameter passing to BacktesterEngine
- **Correct**: Use DataFeeder first, then pass to BacktesterEngine
- **Pattern**:
  ```python
  data_feeder = DataFeeder(data_dir, symbols, timeframes, start_date, end_date)
  backtester = BacktesterEngine(data_feeder=data_feeder, strategy=strategy)

  🎯 File Structure (NON-NEGOTIABLE) 
Step 1: File Naming 

✅ CORRECT: Strategy_mystategy.py
❌ WRONG: mystategy.py, MyStrategy.py, strategy_mystategy.py 
Step 2: File Location 

📁 simple_strategy/strategies/Strategy_mystategy.py 
📝 Template Structure (Copy-Paste This) 

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
from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold  # Add signals you need
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRITICAL: STRATEGY_PARAMETERS (GUI Configuration)
# This dictionary defines what parameters appear in the GUI for users to configure
# Place this at the TOP after imports for better code organization
STRATEGY_PARAMETERS = {
    'indicator_period': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 50,
        'description': 'Primary indicator period',
        'gui_hint': 'Standard values: 14 for RSI, 20/50 for SMAs'
    },
    'overbought_level': {
        'type': 'int',
        'default': 70,
        'min': 60,
        'max': 90,
        'description': 'Overbought threshold for sell signals',
        'gui_hint': 'Higher values = more conservative sells'
    },
    'oversold_level': {
        'type': 'int',
        'default': 30,
        'min': 10,
        'max': 40,
        'description': 'Oversold threshold for buy signals',
        'gui_hint': 'Lower values = more conservative buys'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    CREATE STRATEGY FUNCTION - Required by GUI
    This function MUST exist and work with StrategyBuilder
    
    Args:
        symbols: List of trading symbols (e.g., ['BTCUSDT'])
        timeframes: List of timeframes (e.g., ['1m', '5m'])
        **params: Strategy parameters from GUI/user input
        
    Returns:
        Built strategy instance ready for backtesting/trading
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
        # ⚠️ IMPORTANT: Use only valid methods: 'majority_vote', 'weighted', 'unanimous'
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
        logger.info(f" - Symbols: {self.symbols}")
        logger.info(f" - Timeframes: {self.timeframes}")
        logger.info(f" - Your Param1: {self.your_param1}")
        logger.info(f" - Your Param2: {self.your_param2}")
    
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
    """Create your strategy instance - OPTIONAL but recommended"""
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
        print(f" - Symbols: {strategy.symbols}")
        print(f" - Timeframes: {strategy.timeframes}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing strategy: {e}")
        return False

# For testing - MUST EXIST
if __name__ == "__main__":
    simple_test()

