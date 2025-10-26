# 🧱 INDICATOR & SIGNAL CHEAT SHEET
## Quick Reference for Strategy Building
---

## 🚫 CRITICAL USAGE NOTES (Learned from Mistakes)
-------------------------------------------

### **⚠️ Bollinger Bands - MOST COMMON ERROR**
```python
# ❌ WRONG - Component parameter doesn't exist
bollinger_bands(data['close'], period=20, std_dev=2, component='upper')

# ✅ CORRECT - Add main indicator, it returns tuple
bb_data = bollinger_bands(data['close'], period=20, std_dev=2)
# Returns: (upper_band, middle_band, lower_band)

# Usage in strategy:
strategy_builder.add_indicator('bb', bollinger_bands, period=20, std_dev=2)

# In signal generation:
bb_data = df['bb'].iloc[-1]
if isinstance(bb_data, (tuple, list)):
    upper_band, middle_band, lower_band = bb_data[0], bb_data[1], bb_data[2]
 
 
 
⚠️ MACD - Component Reference 
python

# ✅ CORRECT - MACD returns tuple but signal references main name
macd_data = macd(data['close'], fast_period=12, slow_period=26)
# Returns: (macd_line, signal_line, histogram)

# In signal rules:
strategy_builder.add_signal_rule('macd_signal', macd_signals,
                                   macd_line='macd',  # Use main indicator name
                                   signal_line='macd')  # Use main indicator name
 
 
 
⚠️ Volume Requirements - Be Realistic 
python

# ❌ TOO STRICT - Rarely met
volume_confirmed = current_volume > volume_sma * 2.0  # 200%

# ✅ MORE REALISTIC - Start here
volume_confirmed = current_volume > volume_sma * 1.1  # 110%

# 🎯 BEST FOR TESTING - Start without volume filter
# volume_confirmed = True  # Remove entirely for initial testing
 
 
 
⚠️ Signal Combination Methods 
python

# 'majority_vote' - At least 50% of signals agree (START WITH THIS)
# 'weighted' - Requires weights parameter (ADVANCED)
# 'unanimous' - ALL signals must agree (TOO STRICT FOR TESTING)

# ❌ WRONG - No weights provided
strategy_builder.set_signal_combination('weighted')

# ✅ CORRECT - With weights
strategy_builder.set_signal_combination('weighted', weights={
    'signal1': 0.6,
    'signal2': 0.4
})

# 🎯 START HERE - Simple majority vote
strategy_builder.set_signal_combination('majority_vote')

📊 INDICATORS QUICK REFERENCE 
📈 Trend Indicators 
python

# Simple Moving Average
sma(data['close'], period=20)
# Use: Trend direction, support/resistance

# Exponential Moving Average
ema(data['close'], period=12)
# Use: Faster trend response

# MACD (Multi-output)
macd(data['close'], fast_period=12, slow_period=26)
# Returns: (macd_line, signal_line, histogram)
# Use: Trend momentum, crossovers

📊 Momentum Indicators 
python

# RSI
rsi(data['close'], period=14)
# Use: Overbought/oversold (70/30), divergence

# Stochastic (Multi-output)
stochastic(data['high'], data['low'], data['close'], k_period=14)
# Returns: (%K, %D)
# Use: Overbought/oversold (80/20)

# Rate of Change
roc(data['close'], period=10)
# Use: Momentum strength
 
 
 
📊 Volatility Indicators 
python

# Average True Range
atr(data['high'], data['low'], data['close'], period=14)
# Use: Volatility measurement, stop-loss placement

# Bollinger Bands (Multi-output) - SEE CRITICAL NOTES ABOVE
bollinger_bands(data['close'], period=20, std_dev=2)
# Returns: (upper_band, middle_band, lower_band)
# Use: Volatility bands, breakouts
 
 
 
📊 Volume Indicators 
python

# On Balance Volume
on_balance_volume(data['close'], data['volume'])
# Use: Volume trend confirmation

# Volume SMA
volume_sma(data['volume'], period=20)
# Use: Volume analysis
 
 
 
📡 SIGNALS QUICK REFERENCE 
🎯 Basic Signals 
python

# Overbought/Oversold
overbought_oversold(indicator, overbought=70, oversold=30)
# Returns: Series with BUY/SELL/HOLD
# Use: RSI, Stochastic strategies

# Moving Average Crossover
ma_crossover(fast_ma, slow_ma)
# Returns: Series with BUY/SELL/HOLD
# Use: Trend following strategies
 
 
 
🎯 Advanced Signals 
python

# MACD Signals
macd_signals(macd_line, signal_line, histogram=None)
# Returns: Series with 1/0/-1
# Use: MACD-based strategies

# Bollinger Bands Signals
bollinger_bands_signals(price, upper_band, lower_band)
# Returns: Series with 1/0/-1
# Use: Breakout strategies

# Stochastic Signals
stochastic_signals(k_percent, d_percent, overbought=80, oversold=20)
# Returns: Series with BUY/SELL/HOLD
# Use: Stochastic strategies
 
 
 
🔀 SIGNAL COMPARISON CHART 
Signal Type
 	
Best For
 	
Market Condition
 	
Complexity
 	
Reliability
 
 overbought_oversold	Range-bound	Sideways markets	Low	Medium 
ma_crossover	Trending	Trending markets	Low	High 
macd_signals	Momentum	Changing trends	Medium	Medium 
bollinger_bands_signals	Breakout	Volatile markets	Medium	Medium 
stochastic_signals	Reversal	Range-bound	Medium	Medium 
 
  
🛠️ COMMON STRATEGY PATTERNS 
📈 Trend Following 
python
# Indicators: SMA, EMA, MACD
# Signals: ma_crossover, macd_signals
# Combination: majority_vote
# Timeframes: 1h, 4h, 1d

strategy_builder.add_indicator('sma_fast', sma, period=20)
strategy_builder.add_indicator('sma_slow', sma, period=50)
strategy_builder.add_signal_rule('trend_signal', ma_crossover,
                                   fast_ma='sma_fast', slow_ma='sma_slow')
strategy_builder.set_signal_combination('majority_vote')
 
 
 
📊 Mean Reversion 
python

# Indicators: RSI, Stochastic, Bollinger Bands
# Signals: overbought_oversold, bollinger_bands_signals
# Combination: weighted
# Timeframes: 15m, 1h

strategy_builder.add_indicator('rsi', rsi, period=14)
strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
strategy_builder.set_signal_combination('majority_vote')  # Start simple
 
 
 
🔄 Momentum 
python

# Indicators: RSI, MACD, ROC
# Signals: macd_signals, overbought_oversold
# Combination: majority_vote
# Timeframes: 5m, 15m, 1h

strategy_builder.add_indicator('rsi', rsi, period=14)
strategy_builder.add_indicator('macd', macd, fast_period=12, slow_period=26)
strategy_builder.add_signal_rule('macd_signal', macd_signals,
                                   macd_line='macd', signal_line='macd')
strategy_builder.set_signal_combination('majority_vote')
 
 
 
📊 Breakout 
python

# Indicators: Bollinger Bands, ATR
# Signals: bollinger_bands_signals
# Combination: majority_vote (start simple)
# Timeframes: 15m, 1h

strategy_builder.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
strategy_builder.add_signal_rule('bb_signal', bollinger_bands_signals,
                                   price='close', upper_band='bb', lower_band='bb')
strategy_builder.set_signal_combination('majority_vote')
 

🎯 STRATEGY RECIPE BOOK - WORKING VERSIONS 
📝 Recipe 1: Basic Trend Following (GUARANTEED TO WORK) 
python

# Ingredients:
# - 1 SMA (fast)
# - 1 SMA (slow)
# - 1 ma_crossover signal
# - majority_vote combination
# - No volume filter

strategy_builder.add_indicator('sma_fast', sma, period=20)
strategy_builder.add_indicator('sma_slow', sma, period=50)
strategy_builder.add_signal_rule('trend_signal', ma_crossover,
                                   fast_ma='sma_fast', slow_ma='sma_slow')
strategy_builder.set_signal_combination('majority_vote')

📝 Recipe 2: RSI Mean Reversion (SIMPLE VERSION) 
python

# Ingredients:
# - 1 RSI
# - 1 overbought_oversold signal
# - Conservative parameters
# - No volume filter

strategy_builder.add_indicator('rsi', rsi, period=14)
strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
strategy_builder.set_signal_combination('majority_vote')

🔄 Recipe 3: MACD Momentum (CORRECTED) 
python

# Ingredients:
# - 1 MACD
# - 1 macd_signals signal
# - Correct component references
# - Majority vote for testing

strategy_builder.add_indicator('macd', macd, fast_period=12, slow_period=26)
strategy_builder.add_signal_rule('macd_signal', macd_signals,
                                   macd_line='macd', signal_line='macd')
strategy_builder.set_signal_combination('majority_vote')

📊 Recipe 4: Bollinger Breakout (CORRECTED) 
python

# Ingredients:
# - 1 Bollinger Bands (main indicator)
# - 1 bollinger_bands_signals signal
# - Proper data extraction
# - No component parameter

strategy_builder.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
strategy_builder.add_signal_rule('bb_signal', bollinger_bands_signals,
                                   price='close', upper_band='bb', lower_band='bb')
strategy_builder.set_signal_combination('majority_vote')
 

🎯 Recipe 5: Multi-Indicator (WITH WEIGHTS) 
python

# Ingredients:
# - Multiple indicators
# - Weighted combination
# - Proper weights provided

strategy_builder.add_indicator('rsi', rsi, period=14)
strategy_builder.add_indicator('macd', macd, fast_period=12, slow_period=26)
strategy_builder.add_indicator('sma_fast', sma, period=20)
strategy_builder.add_indicator('sma_slow', sma, period=50)

strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
strategy_builder.add_signal_rule('macd_signal', macd_signals,
                                   macd_line='macd', signal_line='macd')
strategy_builder.add_signal_rule('sma_cross', ma_crossover,
                                   fast_ma='sma_fast', slow_ma='sma_slow')

strategy_builder.set_signal_combination('weighted', weights={
    'rsi_signal': 0.3,
    'macd_signal': 0.4,
    'sma_cross': 0.3
})

🚀 QUICK START TEMPLATES 
📝 Template 1: Ultra-Simple (GUARANTEED WORKING) 
python

# Copy-paste this for a basic working strategy
strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_signal_rule('signal', overbought_oversold,
                           indicator='rsi', overbought=70, oversold=30)
strategy.set_signal_combination('majority_vote')
return strategy.build()

📝 Template 2: Multi-Indicator (WORKING VERSION) 
python

# Copy-paste this for a multi-indicator strategy
strategy = StrategyBuilder(['BTCUSDT'], ['1h', '4h'])
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_indicator('macd', macd, fast_period=12, slow_period=26)
strategy.add_indicator('sma_fast', sma, period=20)
strategy.add_indicator('sma_slow', sma, period=50)

strategy.add_signal_rule('rsi_signal', overbought_oversold,
                           indicator='rsi', overbought=70, oversold=30)
strategy.add_signal_rule('macd_signal', macd_signals,
                           macd_line='macd', signal_line='macd')
strategy.add_signal_rule('sma_cross', ma_crossover,
                           fast_ma='sma_fast', slow_ma='sma_slow')

strategy.set_signal_combination('majority_vote')  # Start with majority_vote
return strategy.build()

📝 Template 3: Multi-Timeframe (WORKING VERSION) 
python

# Copy-paste this for multi-timeframe strategy
strategy = StrategyBuilder(['BTCUSDT'], ['1m', '5m'])

# For 1m entries
strategy.add_indicator('ema_fast_1m', ema, period=9)
strategy.add_indicator('ema_slow_1m', ema, period=21)

# For 5m trend
strategy.add_indicator('ema_trend_5m', ema, period=50)

strategy.add_signal_rule('entry_signal', ma_crossover,
                           fast_ma='ema_fast_1m', slow_ma='ema_slow_1m')

strategy.set_signal_combination('majority_vote')
return strategy.build()

# In signal generation:
if '5m' in all_data.get(symbol, {}):
    trend_ema = all_data[symbol]['5m']['ema_trend_5m'].iloc[-1]
    current_price = all_data[symbol]['5m']['close'].iloc[-1]
    bullish_trend = current_price > trend_ema

⚠️ CRITICAL ERROR PREVENTION 
🚫 Import Errors 
python

# ❌ WRONG - Missing imports
from simple_strategy.strategies.indicators_library import ema
# Missing rsi, atr, volume_sma that you use

# ✅ CORRECT - Import ALL indicators you use
from simple_strategy.strategies.indicators_library import ema, rsi, atr, volume_sma, bollinger_bands
 
 
 
🚫 Signal Rule Requirements 
python

# ❌ WRONG - No signal rules
# StrategyBuilder will fail: "No signal rules defined"

# ✅ CORRECT - Always add at least one signal rule
strategy_builder.add_signal_rule('signal_name', signal_function, ...)

🚫 Class Name Errors 
python

# ❌ WRONG - Space in class name
class SimpleEMA RSIStrategy:  # Syntax error

# ✅ CORRECT - CamelCase without spaces
class SimpleEMARSIStrategy:

🚫 Zero Trades Prevention 
python

# If you get zero trades, check:
# 1. Entry conditions too strict?
# 2. Volume requirements too high?
# 3. Signal combination too restrictive?
# 4. Multi-timeframe data available?

# Start with this ultra-simple test:
strategy_builder.add_indicator('rsi', rsi, period=14)
strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                   indicator='rsi', overbought=70, oversold=30)
strategy_builder.set_signal_combination('majority_vote')
 
 
 
🎯 SUCCESS CHECKLIST 

Before running your strategy, verify: 

     All indicators imported?
     At least one signal rule added?
     Class names correct (no spaces)?
     Bollinger Bands used correctly?
     MACD references correct?
     Signal combination appropriate?
     Volume requirements realistic?
     Multi-timeframe data validated?
     

Remember: Start simple, ensure it works, then add complexity! 