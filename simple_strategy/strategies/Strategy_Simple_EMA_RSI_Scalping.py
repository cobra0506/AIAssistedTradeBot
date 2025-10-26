"""
Simple EMA RSI Scalping Strategy
=================================

A simple but effective scalping strategy that actually generates trades:
- Uses only EMA crossover for trend direction
- Uses RSI for overbought/oversold confirmation
- No volume confirmation (works with low volume periods)
- No multi-timeframe complexity
- Single timeframe focus

Strategy Logic:
1. BULLISH: Fast EMA > Slow EMA AND RSI < 70 = BUY
2. BEARISH: Fast EMA < Slow EMA AND RSI > 30 = SELL
3. EXIT: Opposite signal or RSI extreme

Best for: Most market conditions, reliable signal generation
Author: AI Assisted TradeBot Team
Date: 2025
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
from simple_strategy.strategies.indicators_library import ema, rsi
from simple_strategy.strategies.signals_library import ma_crossover, overbought_oversold
from simple_strategy.shared.strategy_base import StrategyBase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CRITICAL: STRATEGY_PARAMETERS for GUI Configuration
STRATEGY_PARAMETERS = {
    # Fast EMA for entry signals
    'fast_ema_period': {
        'type': 'int',
        'default': 9,
        'min': 5,
        'max': 20,
        'description': 'Fast EMA period for entry signals',
        'gui_hint': 'Lower values = more sensitive entries. Recommended: 8-12'
    },
    # Slow EMA for trend direction
    'slow_ema_period': {
        'type': 'int',
        'default': 21,
        'min': 15,
        'max': 50,
        'description': 'Slow EMA period for trend direction',
        'gui_hint': 'Higher values = smoother trend. Recommended: 20-25'
    },
    # RSI for momentum confirmation
    'rsi_period': {
        'type': 'int',
        'default': 14,
        'min': 7,
        'max': 21,
        'description': 'RSI period for momentum confirmation',
        'gui_hint': 'Standard values: 14, 10 for faster signals'
    },
    # RSI levels - less extreme for more signals
    'rsi_overbought': {
        'type': 'int',
        'default': 65,
        'min': 60,
        'max': 75,
        'description': 'RSI overbought level for sell signals',
        'gui_hint': 'Lower = more sell signals'
    },
    'rsi_oversold': {
        'type': 'int',
        'default': 35,
        'min': 25,
        'max': 40,
        'description': 'RSI oversold level for buy signals',
        'gui_hint': 'Higher = more buy signals'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """
    CREATE STRATEGY FUNCTION - Required by GUI
    """
    # DEBUG: Log what we receive
    logger.info(f"🔧 create_strategy called with:")
    logger.info(f" - symbols: {symbols}")
    logger.info(f" - timeframes: {timeframes}")
    logger.info(f" - params: {params}")
    
    # CRITICAL: Handle None/empty values with defaults
    if symbols is None or len(symbols) == 0:
        logger.warning("⚠️ No symbols provided, using default: ['BTCUSDT']")
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        logger.warning("⚠️ No timeframes provided, using default: ['5m']")
        timeframes = ['5m']
    
    # Get parameters with defaults from STRATEGY_PARAMETERS
    fast_ema_period = params.get('fast_ema_period', 9)
    slow_ema_period = params.get('slow_ema_period', 21)
    rsi_period = params.get('rsi_period', 14)
    rsi_overbought = params.get('rsi_overbought', 65)
    rsi_oversold = params.get('rsi_oversold', 35)
    
    logger.info(f"🎯 Creating Simple EMA RSI strategy with parameters:")
    logger.info(f" - Symbols: {symbols}")
    logger.info(f" - Timeframes: {timeframes}")
    logger.info(f" - Fast EMA: {fast_ema_period}, Slow EMA: {slow_ema_period}")
    logger.info(f" - RSI: {rsi_period} (OB: {rsi_overbought}, OS: {rsi_oversold})")
    
    try:
        # Create strategy using StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # Add indicators for each timeframe
        for timeframe in timeframes:
            # Trend indicators
            strategy_builder.add_indicator(f'ema_fast_{timeframe}', ema, period=fast_ema_period)
            strategy_builder.add_indicator(f'ema_slow_{timeframe}', ema, period=slow_ema_period)
            
            # Momentum indicator
            strategy_builder.add_indicator(f'rsi_{timeframe}', rsi, period=rsi_period)
        
        # Add signal rules
        entry_timeframe = timeframes[0]
        
        # 1. EMA Crossover Signal
        strategy_builder.add_signal_rule('ema_crossover', ma_crossover,
                                       fast_ma=f'ema_fast_{entry_timeframe}',
                                       slow_ma=f'ema_slow_{entry_timeframe}')
        
        # 2. RSI Overbought/Oversold Signal
        strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator=f'rsi_{entry_timeframe}',
                                       overbought=rsi_overbought,
                                       oversold=rsi_oversold)
        
        # Set signal combination method - either signal is fine
        strategy_builder.set_signal_combination('majority_vote')
        
        # Set strategy information
        strategy_builder.set_strategy_info('Simple_EMA_RSI_Scalping', '1.0.0')
        
        # Build and return the strategy
        strategy = strategy_builder.build()
        
        logger.info(f"✅ Simple EMA RSI strategy created successfully!")
        logger.info(f" - Strategy Name: {strategy.name}")
        logger.info(f" - Strategy Symbols: {strategy.symbols}")
        logger.info(f" - Strategy Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        logger.error(f"❌ Error creating Simple EMA RSI strategy: {e}")
        import traceback
        traceback.print_exc()
        raise

class SimpleEMARSIStrategy(StrategyBase):
    """
    Simple EMA RSI Strategy Class
    """
    
    def __init__(self, symbols: List[str], timeframes: List[str], config: Dict[str, Any]):
        super().__init__(
            name="Simple_EMA_RSI_Scalping",
            symbols=symbols,
            timeframes=timeframes,
            config=config
        )
        
        # Strategy-specific parameters
        self.fast_ema_period = config.get('fast_ema_period', 9)
        self.slow_ema_period = config.get('slow_ema_period', 21)
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_overbought = config.get('rsi_overbought', 65)
        self.rsi_oversold = config.get('rsi_oversold', 35)
        
        # Validate parameters
        self._validate_parameters()
        
        logger.info(f"📈 SimpleEMARSIStrategy initialized:")
        logger.info(f" - Symbols: {self.symbols}")
        logger.info(f" - Timeframes: {self.timeframes}")
    
    def _validate_parameters(self):
        """Validate strategy parameters"""
        if self.fast_ema_period >= self.slow_ema_period:
            raise ValueError("Fast EMA period must be less than slow EMA period")
        if self.rsi_oversold >= self.rsi_overbought:
            raise ValueError("RSI oversold level must be less than overbought level")
    
    def calculate_position_size(self, symbol: str, current_price: float = None, signal_strength: float = 1.0) -> float:
        """Simple fixed position size"""
        return 0.001  # Fixed small position for testing
    
    def generate_signals(self, data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Dict[str, str]]:
        """Generate trading signals"""
        signals = {}
        
        try:
            for symbol in data:
                signals[symbol] = {}
                
                for timeframe in data[symbol]:
                    signal = self._generate_single_signal(data[symbol][timeframe], symbol, timeframe)
                    signals[symbol][timeframe] = signal
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return signals
    
    def _generate_single_signal(self, df: pd.DataFrame, symbol: str, timeframe: str) -> str:
        """Generate a single trading signal"""
        try:
            if len(df) < max(self.slow_ema_period, self.rsi_period):
                return 'HOLD'
            
            # Get current values
            current_close = df['close'].iloc[-1]
            current_rsi = df[f'rsi_{timeframe}'].iloc[-1] if f'rsi_{timeframe}' in df.columns else 50
            
            # Get EMAs
            ema_fast = df[f'ema_fast_{timeframe}'].iloc[-1]
            ema_slow = df[f'ema_slow_{timeframe}'].iloc[-1]
            
            # Simple logic - no volume, no multi-timeframe, no strict filters
            
            # Bullish: Fast EMA above Slow EMA AND RSI not overbought
            if ema_fast > ema_slow and current_rsi < self.rsi_overbought:
                return 'BUY'
            
            # Bearish: Fast EMA below Slow EMA AND RSI not oversold
            elif ema_fast < ema_slow and current_rsi > self.rsi_oversold:
                return 'SELL'
            
            return 'HOLD'
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol} {timeframe}: {e}")
            return 'HOLD'

def create_simple_ema_rsi_instance(symbols=None, timeframes=None, **params):
    """Create simple EMA RSI strategy instance"""
    try:
        if symbols is None:
            symbols = ['BTCUSDT']
        if timeframes is None:
            timeframes = ['5m']
        
        strategy = SimpleEMARSIStrategy(symbols, timeframes, params)
        logger.info(f"✅ Simple EMA RSI strategy created successfully")
        return strategy
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise

def simple_test():
    """Simple test to verify the strategy works"""
    try:
        strategy = create_strategy(
            symbols=['BTCUSDT'],
            timeframes=['5m'],
            fast_ema_period=9,
            slow_ema_period=21,
            rsi_period=14,
            rsi_overbought=65,
            rsi_oversold=35
        )
        
        print(f"✅ Simple EMA RSI strategy created successfully: {strategy.name}")
        print(f" - Symbols: {strategy.symbols}")
        print(f" - Timeframes: {strategy.timeframes}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Simple EMA RSI strategy: {e}")
        return False

# For testing
if __name__ == "__main__":
    simple_test()