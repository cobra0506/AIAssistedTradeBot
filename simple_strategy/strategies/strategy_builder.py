
```python
"""
Strategy Builder - Ultimate Strategy Creation System
===================================================

This system allows you to create ANY trading strategy by combining indicators,
signals, and risk management rules. No limitations, no templates - pure flexibility!

Author: AI Assisted TradeBot Team
Date: 2025
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union, Callable
import logging
from simple_strategy.shared.strategy_base import StrategyBase

logger = logging.getLogger(__name__)


class StrategyBuilder:
    """
    Ultimate Strategy Builder - Create ANY trading strategy you can imagine!
    """
    
    def __init__(self, symbols: List[str], timeframes: List[str] = ['1m']):
        """
        Initialize the Strategy Builder
        
        Args:
            symbols: List of trading symbols
            timeframes: List of timeframes
        """
        self.symbols = symbols
        self.timeframes = timeframes
        
        # Strategy components
        self.indicators = {}  # {name: (function, params, timeframe)}
        self.signal_rules = {}  # {name: (function, params)}
        self.risk_rules = {}  # {rule_type: params}
        self.signal_combination = 'majority_vote'  # or 'weighted', 'unanimous'
        self.signal_weights = {}  # for weighted combination
        
        # Strategy metadata
        self.strategy_name = "CustomStrategy"
        self.version = "1.0.0"
        
        logger.info(f"🏗️ Strategy Builder initialized for {symbols} on {timeframes}")
    
    def add_indicator(self, name: str, indicator_func: Callable, 
                     timeframe: str = None, **params) -> 'StrategyBuilder':
        """
        Add an indicator to the strategy
        
        Args:
            name: Indicator name (for reference)
            indicator_func: Indicator function from indicators_library
            timeframe: Specific timeframe (optional)
            **params: Indicator parameters
            
        Returns:
            Self for method chaining
        """
        try:
            self.indicators[name] = {
                'function': indicator_func,
                'params': params,
                'timeframe': timeframe
            }
            logger.debug(f"📊 Added indicator: {name} with params: {params}")
            return self
        except Exception as e:
            logger.error(f"❌ Error adding indicator {name}: {e}")
            return self
    
    def add_signal_rule(self, name: str, signal_func: Callable, **params) -> 'StrategyBuilder':
        """
        Add a signal rule to the strategy
        
        Args:
            name: Signal rule name
            signal_func: Signal function from signals_library
            **params: Signal parameters
            
        Returns:
            Self for method chaining
        """
        try:
            self.signal_rules[name] = {
                'function': signal_func,
                'params': params
            }
            logger.debug(f"📈 Added signal rule: {name} with params: {params}")
            return self
        except Exception as e:
            logger.error(f"❌ Error adding signal rule {name}: {e}")
            return self
    
    def add_risk_rule(self, rule_type: str, **params) -> 'StrategyBuilder':
        """
        Add a risk management rule
        
        Args:
            rule_type: Rule type ('stop_loss', 'take_profit', 'max_position_size', etc.)
            **params: Rule parameters
            
        Returns:
            Self for method chaining
        """
        try:
            self.risk_rules[rule_type] = params
            logger.debug(f"🛡️ Added risk rule: {rule_type} with params: {params}")
            return self
        except Exception as e:
            logger.error(f"❌ Error adding risk rule {rule_type}: {e}")
            return self
    
    def set_signal_combination(self, method: str, **kwargs) -> 'StrategyBuilder':
        """
        Set how signals should be combined
        
        Args:
            method: Combination method ('majority_vote', 'weighted', 'unanimous')
            **kwargs: Additional parameters (like weights for weighted method)
            
        Returns:
            Self for method chaining
        """
        try:
            self.signal_combination = method
            if method == 'weighted' and 'weights' in kwargs:
                self.signal_weights = kwargs['weights']
            logger.debug(f"🔀 Set signal combination method: {method}")
            return self
        except Exception as e:
            logger.error(f"❌ Error setting signal combination: {e}")
            return self
    
    def set_strategy_info(self, name: str, version: str = "1.0.0") -> 'StrategyBuilder':
        """
        Set strategy information
        
        Args:
            name: Strategy name
            version: Strategy version
            
        Returns:
            Self for method chaining
        """
        self.strategy_name = name
        self.version = version
        logger.debug(f"📝 Set strategy info: {name} v{version}")
        return self
    
    def build(self) -> StrategyBase:
        """
        Build the complete strategy
        
        Returns:
            Complete strategy class that inherits from StrategyBase
        """
        try:
            logger.info(f"🔨 Building strategy: {self.strategy_name}")
            
            # Create the strategy class
            class BuiltStrategy(StrategyBase):
                def __init__(self, symbols, timeframes):
                    super().__init__(symbols, timeframes)
                    self.strategy_name = self.strategy_name
                    self.version = self.version
                    
                    # Copy all components from builder
                    self.indicators = self.indicators.copy()
                    self.signal_rules = self.signal_rules.copy()
                    self.risk_rules = self.risk_rules.copy()
                    self.signal_combination = self.signal_combination
                    self.signal_weights = self.signal_weights.copy()
                    
                    # Strategy state
                    self.calculated_indicators = {}
                    self.generated_signals = {}
                
                def generate_signals(self, data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Dict[str, str]]:
                    """Generate trading signals using the building block system"""
                    signals = {}
                    
                    for symbol in self.symbols:
                        signals[symbol] = {}
                        
                        for timeframe in self.timeframes:
                            if symbol not in data or timeframe not in data[symbol]:
                                continue
                            
                            df = data[symbol][timeframe].copy()
                            
                            # Calculate all indicators
                            indicator_results = self._calculate_indicators(df, symbol, timeframe)
                            
                            # Generate signals from indicators
                            signal_results = self._generate_signals_from_indicators(indicator_results)
                            
                            # Combine signals
                            combined_signal = self._combine_signals(signal_results)
                            
                            signals[symbol][timeframe] = combined_signal
                    
                    return signals
                
                def _calculate_indicators(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
                    """Calculate all indicators for the given data"""
                    results = {}
                    
                    for name, config in self.indicators.items():
                        try:
                            func = config['function']
                            params = config['params']
                            indicator_timeframe = config.get('timeframe')
                            
                            # Skip if indicator is for a different timeframe
                            if indicator_timeframe and indicator_timeframe != timeframe:
                                continue
                            
                            # Handle different indicator functions
                            if name in ['stochastic', 'srsi', 'macd', 'bollinger_bands']:
                                # Multi-output indicators
                                if name == 'stochastic':
                                    result = func(df['high'], df['low'], df['close'], **params)
                                elif name == 'srsi':
                                    result = func(df['close'], **params)
                                elif name == 'macd':
                                    result = func(df['close'], **params)
                                elif name == 'bollinger_bands':
                                    result = func(df['close'], **params)
                                results[name] = result
                            else:
                                # Single-output indicators
                                if name in ['atr', 'cci', 'williams_r']:
                                    result = func(df['high'], df['low'], df['close'], **params)
                                elif name == 'on_balance_volume':
                                    result = func(df['close'], df['volume'], **params)
                                elif name == 'volume_sma':
                                    result = func(df['volume'], **params)
                                else:
                                    result = func(df['close'], **params)
                                results[name] = result
                            
                            logger.debug(f"📊 Calculated {name} for {symbol} {timeframe}")
                            
                        except Exception as e:
                            logger.error(f"❌ Error calculating {name}: {e}")
                    
                    return results
                
                def _generate_signals_from_indicators(self, indicators: Dict[str, Any]) -> Dict[str, pd.Series]:
                    """Generate signals from calculated indicators"""
                    signals = {}
                    
                    for rule_name, config in self.signal_rules.items():
                        try:
                            func = config['function']
                            params = config['params']
                            
                            # Prepare arguments for signal function
                            args = []
                            for param_name, param_value in params.items():
                                if param_name in indicators:
                                    args.append(indicators[param_name])
                                else:
                                    args.append(param_value)
                            
                            # Generate signal
                            signal_result = func(*args)
                            signals[rule_name] = signal_result
                            
                            logger.debug(f"📈 Generated {rule_name} signal")
                            
                        except Exception as e:
                            logger.error(f"❌ Error generating {rule_name} signal: {e}")
                    
                    return signals
                
                def _combine_signals(self, signals: Dict[str, pd.Series]) -> str:
                    """Combine multiple signals into one final signal"""
                    if not signals:
                        return 'HOLD'
                    
                    try:
                        if self.signal_combination == 'majority_vote':
                            return self._majority_vote_combination(signals)
                        elif self.signal_combination == 'weighted':
                            return self._weighted_combination(signals)
                        elif self.signal_combination == 'unanimous':
                            return self._unanimous_combination(signals)
                        else:
                            # Default to first signal
                            first_signal = next(iter(signals.values()))
                            if len(first_signal) > 0:
                                latest_signal = first_signal.iloc[-1]
                                return 'BUY' if latest_signal == 1 else 'SELL' if latest_signal == -1 else 'HOLD'
                            return 'HOLD'
                            
                    except Exception as e:
                        logger.error(f"❌ Error combining signals: {e}")
                        return 'HOLD'
                
                def _majority_vote_combination(self, signals: Dict[str, pd.Series]) -> str:
                    """Combine signals using majority vote"""
                    if not signals:
                        return 'HOLD'
                    
                    # Get latest signals
                    latest_signals = []
                    for signal_series in signals.values():
                        if len(signal_series) > 0:
                            latest_signals.append(signal_series.iloc[-1])
                    
                    if not latest_signals:
                        return 'HOLD'
                    
                    # Count votes
                    buy_votes = latest_signals.count(1)
                    sell_votes = latest_signals.count(-1)
                    hold_votes = latest_signals.count(0)
                    
                    # Majority vote
                    if buy_votes > sell_votes and buy_votes > hold_votes:
                        return 'BUY'
                    elif sell_votes > buy_votes and sell_votes > hold_votes:
                        return 'SELL'
                    else:
                        return 'HOLD'
                
                def _weighted_combination(self, signals: Dict[str, pd.Series]) -> str:
                    """Combine signals using weighted average"""
                    if not signals:
                        return 'HOLD'
                    
                    weighted_sum = 0.0
                    total_weight = 0.0
                    
                    for rule_name, signal_series in signals.items():
                        if len(signal_series) > 0:
                            weight = self.signal_weights.get(rule_name, 1.0)
                            weighted_sum += signal_series.iloc[-1] * weight
                            total_weight += weight
                    
                    if total_weight == 0:
                        return 'HOLD'
                    
                    weighted_avg = weighted_sum / total_weight
                    
                    if weighted_avg > 0.3:
                        return 'BUY'
                    elif weighted_avg < -0.3:
                        return 'SELL'
                    else:
                        return 'HOLD'
                
                def _unanimous_combination(self, signals: Dict[str, pd.Series]) -> str:
                    """Combine signals requiring unanimous agreement"""
                    if not signals:
                        return 'HOLD'
                    
                    latest_signals = []
                    for signal_series in signals.values():
                        if len(signal_series) > 0:
                            latest_signals.append(signal_series.iloc[-1])
                    
                    if not latest_signals:
                        return 'HOLD'
                    
                    # Check if all signals agree
                    if all(signal == 1 for signal in latest_signals):
                        return 'BUY'
                    elif all(signal == -1 for signal in latest_signals):
                        return 'SELL'
                    else:
                        return 'HOLD'
                
                def calculate_position_size(self, symbol: str, signal: str, 
                                          current_price: float, account_balance: float) -> float:
                    """Calculate position size based on risk rules"""
                    if signal == 'HOLD':
                        return 0.0
                    
                    try:
                        # Get max position size from risk rules
                        max_position_pct = self.risk_rules.get('max_position_size', {}).get('percent', 10.0)
                        max_position_amount = account_balance * (max_position_pct / 100.0)
                        
                        # Calculate position size
                        position_size = max_position_amount / current_price
                        
                        logger.debug(f"🔧 {symbol} position size: {position_size:.4f}")
                        return position_size
                        
                    except Exception as e:
                        logger.error(f"❌ Error calculating position size: {e}")
                        return 0.0
                
                def get_stop_loss_take_profit(self, symbol: str, signal: str, 
                                           entry_price: float) -> Tuple[float, float]:
                    """Calculate stop loss and take profit levels"""
                    try:
                        stop_loss_pct = self.risk_rules.get('stop_loss', {}).get('percent', 2.0)
                        take_profit_pct = self.risk_rules.get('take_profit', {}).get('percent', 4.0)
                        
                        if signal == 'BUY':
                            stop_loss = entry_price * (1 - stop_loss_pct / 100.0)
                            take_profit = entry_price * (1 + take_profit_pct / 100.0)
                        elif signal == 'SELL':
                            stop_loss = entry_price * (1 + stop_loss_pct / 100.0)
                            take_profit = entry_price * (1 - take_profit_pct / 100.0)
                        else:
                            stop_loss = entry_price
                            take_profit = entry_price
                        
                        logger.debug(f"🔧 {symbol} SL/TP: SL={stop_loss:.2f}, TP={take_profit:.2f}")
                        return stop_loss, take_profit
                        
                    except Exception as e:
                        logger.error(f"❌ Error calculating SL/TP: {e}")
                        return entry_price, entry_price
                
                def get_strategy_info(self) -> Dict:
                    """Get strategy information"""
                    return {
                        'strategy_name': self.strategy_name,
                        'version': self.version,
                        'symbols': self.symbols,
                        'timeframes': self.timeframes,
                        'indicators': list(self.indicators.keys()),
                        'signal_rules': list(self.signal_rules.keys()),
                        'risk_rules': self.risk_rules,
                        'signal_combination': self.signal_combination,
                        'signal_weights': self.signal_weights
                    }
            
            # Create and return the strategy instance
            strategy_instance = BuiltStrategy(self.symbols, self.timeframes)
            strategy_instance.strategy_name = self.strategy_name
            strategy_instance.version = self.version
            strategy_instance.indicators = self.indicators
            strategy_instance.signal_rules = self.signal_rules
            strategy_instance.risk_rules = self.risk_rules
            strategy_instance.signal_combination = self.signal_combination
            strategy_instance.signal_weights = self.signal_weights
            
            logger.info(f"✅ Strategy '{self.strategy_name}' built successfully!")
            return strategy_instance
            
        except Exception as e:
            logger.error(f"❌ Error building strategy: {e}")
            raise


# === EXAMPLE USAGE ===
if __name__ == "__main__":
    """
    Example of how to use the Strategy Builder
    """
    
    # Import libraries
    from simple_strategy.strategies.indicators_library import rsi, sma, macd
    from simple_strategy.strategies.signals_library import overbought_oversold, ma_crossover, macd_signals
    
    # Example 1: Simple RSI Strategy
    print("🎯 Example 1: Simple RSI Strategy")
    strategy1 = StrategyBuilder(['BTCUSDT'], ['1m'])
    strategy1.add_indicator('rsi', rsi, period=14)
    strategy1.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    strategy1.add_risk_rule('stop_loss', percent=2.0)
    strategy1.add_risk_rule('take_profit', percent=4.0)
    strategy1.set_strategy_info('SimpleRSI', '1.0.0')
    
    simple_rsi = strategy1.build()
    print(f"✅ Built strategy: {simple_rsi.get_strategy_info()['strategy_name']}")
    
    # Example 2: Multi-Indicator Strategy
    print("\n🎯 Example 2: Multi-Indicator Strategy")
    strategy2 = StrategyBuilder(['BTCUSDT', 'ETHUSDT'], ['1m', '5m'])
    strategy2.add_indicator('rsi', rsi, period=14)
    strategy2.add_indicator('sma_short', sma, period=20)
    strategy2.add_indicator('sma_long', sma, period=50)
    strategy2.add_indicator('macd', macd, fast_period=12, slow_period=26)
    
    strategy2.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    strategy2.add_signal_rule('ma_cross', ma_crossover)
    strategy2.add_signal_rule('macd_signal', macd_signals)
    
    strategy2.set_signal_combination('majority_vote')
    strategy2.add_risk_rule('stop_loss', percent=1.5)
    strategy2.add_risk_rule('take_profit', percent=3.0)
    strategy2.set_strategy_info('MultiIndicator', '1.0.0')
    
    multi_indicator = strategy2.build()
    print(f"✅ Built strategy: {multi_indicator.get_strategy_info()['strategy_name']}")
    
    # Example 3: Weighted Strategy
    print("\n🎯 Example 3: Weighted Strategy")
    strategy3 = StrategyBuilder(['BTCUSDT'], ['1m'])
    strategy3.add_indicator('rsi', rsi, period=14)
    strategy3.add_indicator('sma_short', sma, period=20)
    strategy3.add_indicator('sma_long', sma, period=50)
    
    strategy3.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
    strategy3.add_signal_rule('ma_cross', ma_crossover)
    
    strategy3.set_signal_combination('weighted', weights={
        'rsi_signal': 0.6,
        'ma_cross': 0.4
    })
    strategy3.set_strategy_info('WeightedStrategy', '1.0.0')
    
    weighted_strategy = strategy3.build()
    print(f"✅ Built strategy: {weighted_strategy.get_strategy_info()['strategy_name']}")
    
    print("\n🎉 All examples completed! Strategy Builder is ready to use!")