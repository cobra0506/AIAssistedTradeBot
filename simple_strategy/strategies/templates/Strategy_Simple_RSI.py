"""
Simple RSI Strategy Template - Ready to Use
Based on Strategy_simple_RSI.py mentioned in your analysis
"""

import sys
import os
import logging
from typing import Dict, List, Any

# Add parent directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import rsi
from simple_strategy.strategies.signals_library import overbought_oversold

logger = logging.getLogger(__name__)

# GUI Parameters
STRATEGY_PARAMETERS = {
    'rsi_period': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 30,
        'description': 'RSI calculation period'
    },
    'overbought': {
        'type': 'int',
        'default': 70,
        'min': 60,
        'max': 85,
        'description': 'RSI overbought level (sell signal)'
    },
    'oversold': {
        'type': 'int',
        'default': 30,
        'min': 15,
        'max': 40,
        'description': 'RSI oversold level (buy signal)'
    }
}

def create_strategy(symbols=None, timeframes=None, **params):
    """Create Simple RSI Strategy"""
    if symbols is None:
        symbols = ['BTCUSDT']
    if timeframes is None:
        timeframes = ['1m']
    
    # Get parameters
    rsi_period = params.get('rsi_period', 14)
    overbought = params.get('overbought', 70)
    oversold = params.get('oversold', 30)
    
    # Create strategy
    strategy_builder = StrategyBuilder(symbols, timeframes)
    strategy_builder.add_indicator('rsi', rsi, period=rsi_period)
    strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi',
                                   overbought=overbought,
                                   oversold=oversold)
    strategy_builder.set_signal_combination('majority_vote')
    strategy_builder.set_strategy_info('SimpleRSI', '1.0.0')
    
    return strategy_builder.build()