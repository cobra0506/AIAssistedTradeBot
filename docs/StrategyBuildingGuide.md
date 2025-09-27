     Check the examples in examples/strategies/ for inspiration
     

 
 
 
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25

### **3. Create StrategyBuildingGuide.md**

```markdown
# Strategy Building Guide
========================

## 🎯 Overview

The Building Block Strategy System allows you to create ANY trading strategy you can imagine by combining indicators, signals, and risk management rules. No limitations, no templates - just pure strategy creativity!

## 🏗️ System Architecture

### Core Components:
1. **Indicators Library** (`indicators_library.py`) - All technical indicators
2. **Signals Library** (`signals_library.py`) - All signal processing functions
3. **Strategy Builder** (`strategy_builder.py`) - Strategy creation engine

## 🚀 Quick Start

### Step 1: Import Components
```python
from simple_strategy.strategies.strategy_builder import StrategyBuilder
from simple_strategy.strategies.indicators_library import *
from simple_strategy.strategies.signals_library import *
 
 
 
Step 2: Create Strategy Builder 
python
 
 
 
1
2
3
4
strategy = StrategyBuilder(
    symbols=['BTCUSDT', 'ETHUSDT'],
    timeframes=['1m', '5m', '15m']
)
 
 
 
Step 3: Add Indicators 
python
 
 
 
1
2
3
4
5
# Add any indicators with any parameters
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_indicator('sma_short', sma, period=20)
strategy.add_indicator('sma_long', sma, period=50)
strategy.add_indicator('macd', macd, fast_period=12, slow_period=26)
 
 
 
Step 4: Add Signal Rules 
python
 
 
 
1
2
3
4
5
# Add any signal logic
strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                        overbought=70, oversold=30)
strategy.add_signal_rule('ma_cross', ma_crossover)
strategy.add_signal_rule('macd_signal', macd_signals)
 
 
 
Step 5: Combine Signals 
python
 
 
 
1
2
# Choose how to combine signals
strategy.set_signal_combination('majority_vote')  # or 'weighted', 'unanimous'
 
 
 
Step 6: Add Risk Management 
python
 
 
 
1
2
3
4
# Add risk management rules
strategy.add_risk_rule('stop_loss', percent=2.0)
strategy.add_risk_rule('take_profit', percent=4.0)
strategy.add_risk_rule('max_position_size', percent=10.0)
 
 
 
Step 7: Build Strategy 
python
 
 
 
1
2
# Create your complete strategy
my_strategy = strategy.build()
 
 
 
📊 Available Indicators 
Trend Indicators: 

     sma(data, period) - Simple Moving Average
     ema(data, period) - Exponential Moving Average
     wma(data, period) - Weighted Moving Average
     dema(data, period) - Double Exponential Moving Average
     tema(data, period) - Triple Exponential Moving Average
     

Momentum Indicators: 

     rsi(data, period) - Relative Strength Index
     stochastic(high, low, close, k_period, d_period) - Stochastic Oscillator
     srsi(data, period, d_period) - Stochastic RSI
     macd(data, fast_period, slow_period, signal_period) - MACD
     cci(high, low, close, period) - Commodity Channel Index
     williams_r(high, low, close, period) - Williams %R
     

Volatility Indicators: 

     bollinger_bands(data, period, std_dev) - Bollinger Bands
     atr(high, low, close, period) - Average True Range
     

Volume Indicators: 

     volume_sma(volume, period) - Volume SMA
     on_balance_volume(close, volume) - On Balance Volume
     

Utility Functions: 

     crossover(series1, series2) - Detect crossover
     crossunder(series1, series2) - Detect crossunder
     highest(data, period) - Highest value over period
     lowest(data, period) - Lowest value over period
     

📈 Available Signal Functions 
Basic Signals: 

     overbought_oversold(indicator, overbought, oversold) - Overbought/oversold signals
     ma_crossover(fast_ma, slow_ma) - Moving average crossover
     macd_signals(macd_line, signal_line, histogram) - MACD signals
     bollinger_bands_signals(price, upper, lower, middle) - Bollinger Bands signals
     stochastic_signals(k_percent, d_percent, overbought, oversold) - Stochastic signals
     

Advanced Signals: 

     divergence_signals(price, indicator, lookback_period) - Divergence detection
     multi_timeframe_confirmation(signals_dict, min_confirmations) - Multi-timeframe confirmation
     breakout_signals(price, resistance, support, penetration_pct) - Breakout signals
     trend_strength_signals(price, short_ma, long_ma, adx, adx_threshold) - Trend strength signals
     

Combination Signals: 

     majority_vote_signals(*signal_series) - Majority vote combination
     weighted_signals(*weighted_signals) - Weighted combination
     

🎯 Strategy Examples 
Example 1: Simple RSI Strategy 
python
 
 
 
1
2
3
4
5
6
strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                        overbought=70, oversold=30)
strategy.add_risk_rule('stop_loss', percent=2.0)
simple_rsi = strategy.build()
 
 
 
Example 2: Multi-Indicator Strategy 
python
 
 
 
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
strategy = StrategyBuilder(['BTCUSDT', 'ETHUSDT'], ['1m', '5m'])
strategy.add_indicator('rsi', rsi, period=14)
strategy.add_indicator('sma_short', sma, period=20)
strategy.add_indicator('sma_long', sma, period=50)
strategy.add_indicator('macd', macd, fast_period=12, slow_period=26)

strategy.add_signal_rule('rsi_signal', overbought_oversold, overbought=70, oversold=30)
strategy.add_signal_rule('ma_cross', ma_crossover)
strategy.add_signal_rule('macd_signal', macd_signals)

strategy.set_signal_combination('majority_vote')
strategy.add_risk_rule('stop_loss', percent=1.5)
strategy.add_risk_rule('take_profit', percent=3.0)

multi_indicator = strategy.build()
 
 
 
Example 3: Advanced Multi-Timeframe Strategy 
python
 
 
 
1
2
3
4
5
6
7
8
9
10
11
12
13
14
strategy = StrategyBuilder(['BTCUSDT'], ['1m', '5m', '15m'])
strategy.add_indicator('rsi_1m', rsi, period=14, timeframe='1m')
strategy.add_indicator('rsi_5m', rsi, period=14, timeframe='5m')
strategy.add_indicator('rsi_15m', rsi, period=14, timeframe='15m')

strategy.add_signal_rule('rsi_1m_signal', overbought_oversold, overbought=70, oversold=30)
strategy.add_signal_rule('rsi_5m_signal', overbought_oversold, overbought=70, oversold=30)
strategy.add_signal_rule('rsi_15m_signal', overbought_oversold, overbought=70, oversold=30)

strategy.set_signal_combination('unanimous')  # All timeframes must agree
strategy.add_risk_rule('stop_loss', percent=1.0)
strategy.add_risk_rule('take_profit', percent=2.0)

advanced_strategy = strategy.build()
 
 
 
🔧 Advanced Features 
Custom Signal Functions: 
python
 
 
 
1
2
3
4
5
6
7
8
⌄
def my_custom_signal(indicator1, indicator2, threshold=50):
    """Custom signal logic"""
    signals = pd.Series(0, index=indicator1.index)
    signals[(indicator1 > threshold) & (indicator2 > threshold)] = 1
    signals[(indicator1 < threshold) & (indicator2 < threshold)] = -1
    return signals

strategy.add_signal_rule('custom_signal', my_custom_signal, threshold=60)
 
 
 
Weighted Signal Combination: 
python
 
 
 
1
2
3
4
5
⌄
strategy.set_signal_combination('weighted', weights={
    'rsi_signal': 0.4,
    'ma_cross': 0.3,
    'macd_signal': 0.3
})
 
 
 
Dynamic Parameters: 
python
 
 
 
1
2
# Parameters can be lists for optimization
strategy.add_indicator('rsi', rsi, period=[14, 21, 28])  # Will test all periods
 
 
 
🧪 Testing Your Strategies 

All strategies created with the Strategy Builder are automatically compatible with your existing backtesting system: 
python
 
 
 
1
2
3
4
5
# Use with your backtesting engine
from simple_strategy.backtester.backtester_engine import BacktesterEngine

backtester = BacktesterEngine(my_strategy)
results = backtester.run_backtest()
 
 
 
📚 Best Practices 

     Start Simple: Begin with basic strategies and gradually add complexity
     Test Thoroughly: Always test strategies with historical data
     Use Risk Management: Always include stop-loss and take-profit rules
     Multi-Timeframe Analysis: Consider multiple timeframes for confirmation
     Parameter Optimization: Test different parameter combinations
     Monitor Performance: Regularly review strategy performance
     

🎉 Next Steps 

     Experiment: Try different indicator combinations
     Optimize: Find optimal parameters for your strategies
     Backtest: Test strategies thoroughly with historical data
     Paper Trade: Test strategies in real-time with paper trading
     Live Trade: Deploy successful strategies to live trading
     
    