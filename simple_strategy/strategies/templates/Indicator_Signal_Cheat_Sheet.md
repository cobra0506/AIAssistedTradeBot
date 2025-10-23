### 📋 **Indicator_Signal_Cheat_Sheet.md:**

```markdown
# 🧱 INDICATOR & SIGNAL CHEAT SHEET
## Quick Reference for Strategy Building

---

## 📊 INDICATORS QUICK REFERENCE

### 📈 **Trend Indicators**
```python
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

# Bollinger Bands (Multi-output)
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
stochastic_signals(k_percent, d_percent)
# Returns: Series with 1/0/-1
# Use: Stochastic strategies
 
 
 
🔀 SIGNAL COMPARISON CHART 
Signal Type
 	
Best For
 	
Market Condition
 	
Complexity
 
 overbought_oversold	Range-bound	Sideways markets	Low 
ma_crossover	Trending	Trending markets	Low 
macd_signals	Momentum	Changing trends	Medium 
bollinger_bands_signals	Breakout	Volatile markets	Medium 
stochastic_signals	Reversal	Range-bound	Medium 
 
  
🛠️ COMMON STRATEGY PATTERNS 
📈 Trend Following 
python

# Indicators: SMA, EMA, MACD
# Signals: ma_crossover, macd_signals
# Combination: majority_vote
# Timeframes: 1h, 4h, 1d
 
 
 
📊 Mean Reversion 
python

# Indicators: RSI, Stochastic, Bollinger Bands
# Signals: overbought_oversold, bollinger_bands_signals
# Combination: weighted
# Timeframes: 15m, 1h
 
 
 
🔄 Momentum 
python

# Indicators: RSI, MACD, ROC
# Signals: macd_signals, overbought_oversold
# Combination: majority_vote
# Timeframes: 5m, 15m, 1h
 
 
 
📊 Breakout 
python

# Indicators: Bollinger Bands, ATR
# Signals: bollinger_bands_signals
# Combination: unanimous
# Timeframes: 15m, 1h
 
 
 
🎯 STRATEGY RECIPE BOOK 
📈 Recipe 1: Basic Trend Following 
python

# Ingredients:
# - 1 SMA (fast)
# - 1 SMA (slow)  
# - 1 ma_crossover signal
# - majority_vote combination

# Instructions:
strategy.add_indicator('sma_fast', sma, period=20)
strategy.add_indicator('sma_slow', sma, period=50)
strategy.add_signal_rule('trend_signal', ma_crossover,
                         fast_ma='sma_fast', slow_ma='sma_slow')
strategy.set_signal_combination('majority_vote')
 
 
 
📊 Recipe 2: RSI Mean Reversion 
python

# Ingredients:
# - 1 RSI
# - 1 overbought_oversold signal
# - Conservative parameters

# Instructions:
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_signal_rule('rsi_signal', overbought_oversold,
                         indicator='rsi', overbought=70, oversold=30)
strategy.set_signal_combination('majority_vote')
 
 
 
🔄 Recipe 3: MACD Momentum 
python

# Ingredients:
# - 1 MACD
# - 1 macd_signals signal
# - Trend confirmation

# Instructions:
strategy.add_indicator('macd', macd, fast_period=12, slow_period=26)
strategy.add_signal_rule('macd_signal', macd_signals,
                         macd_line='macd', signal_line='macd')
strategy.set_signal_combination('majority_vote')
 
 
 
📊 Recipe 4: Bollinger Breakout 
python

# Ingredients:
# - 1 Bollinger Bands
# - 1 bollinger_bands_signals signal
# - Volatility filter

# Instructions:
strategy.add_indicator('bb', bollinger_bands, period=20, std_dev=2)
strategy.add_signal_rule('bb_signal', bollinger_bands_signals,
                         price='price', upper_band='bb', lower_band='bb')
strategy.set_signal_combination('majority_vote')
 
 
 
🎯 Recipe 5: Multi-Indicator Confirmation 
python

# Ingredients:
# - 1 RSI
# - 1 MACD
# - 1 SMA crossover
# - Weighted combination

# Instructions:
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

strategy.set_signal_combination('weighted', weights={
    'rsi_signal': 0.3,
    'macd_signal': 0.4,
    'sma_cross': 0.3
})
 
 
 
🚀 QUICK START TEMPLATES 
📝 Template 1: Ultra-Simple 
python

# Copy-paste this for a basic working strategy
strategy = StrategyBuilder(['BTCUSDT'], ['1h'])
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_signal_rule('signal', overbought_oversold,
                         indicator='rsi', overbought=70, oversold=30)
strategy.set_signal_combination('majority_vote')
strategy.add_risk_rule('stop_loss', percent=2.0)
strategy.add_risk_rule('take_profit', percent=4.0)
return strategy.build()
 
 
 
📝 Template 2: Multi-Indicator 
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

strategy.set_signal_combination('weighted', weights={
    'rsi_signal': 0.3,
    'macd_signal': 0.4,
    'sma_cross': 0.3
})

strategy.add_risk_rule('stop_loss', percent=1.5)
strategy.add_risk_rule('take_profit', percent=3.0)
return strategy.build()
 
 
 
🎯 TROUBLESHOOTING QUICK GUIDE 
❌ No Trades Generated? 

     Check signal combination (avoid "unanimous")
     Verify indicator parameters
     Ensure signals are not too restrictive
     

❌ Too Many Trades? 

     Add confirmation indicators
     Use more conservative parameters
     Increase signal combination requirements
     

❌ Poor Performance? 

     Check market condition match
     Optimize parameters systematically
     Add proper risk management
     

❌ Errors During Backtest? 

     Verify indicator function signatures
     Check parameter types and ranges
     Ensure all required data is available
     

🚀 Happy Strategy Building! 