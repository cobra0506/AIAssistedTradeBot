Here's a complete, self-contained documentation that should work with any AI: 
markdown
 
 
 
1
2
3
⌄
# 100% Foolproof Strategy Creation Guide

## Project Structure (EXACT)
 
 
 

AIAssistedTradeBot/
├── main.py
├── simple_strategy/
│   ├── strategies/
│   │   ├── strategy_builder.py
│   │   ├── indicators_library.py
│   │   ├── signals_library.py
│   │   └── shared/
│   │       └── strategy_base.py
│   └── backtester/
└── docs/ 
 
 
 
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
107
108
109
110
111
112
113
114
115
116
117
118
119
120
121
122
123
124
125
126
127
128
129
130
131
132
133
134
135
136
137
138
139
140
141
142
143
144
145
146
147
148
149
150
151
152
153
154
155
156
157
158
159
160
        strategy_builder.set_signal_combination('majority_vote')
        
        # EXACT Strategy Info (DO NOT CHANGE)
        strategy_builder.set_strategy_info('My_Strategy', '1.0.0')
        
        # EXACT Strategy Building (DO NOT CHANGE)
        strategy = strategy_builder.build()
        
        # EXACT Success Logging (DO NOT CHANGE)
        logger.info(f"✅ Strategy created successfully!")
        logger.info(f"   - Strategy Name: {strategy.name}")
        logger.info(f"   - Strategy Symbols: {strategy.symbols}")
        logger.info(f"   - Strategy Timeframes: {strategy.timeframes}")
        
        return strategy
        
    except Exception as e:
        # EXACT Error Handling (DO NOT CHANGE)
        logger.error(f"❌ Error creating strategy: {e}")
        import traceback
        traceback.print_exc()
        raise

# EXACT Parameters Dictionary (DO NOT CHANGE name or structure)
STRATEGY_PARAMETERS = {
    'fast_period': {
        'type': 'int',
        'default': 20,
        'min': 5,
        'max': 100,
        'description': 'Fast moving average period',
        'gui_hint': 'Higher values = fewer signals. Recommended: 20'
    },
    'slow_period': {
        'type': 'int',
        'default': 50,
        'min': 20,
        'max': 200,
        'description': 'Slow moving average period',
        'gui_hint': 'Higher values = stronger trends. Recommended: 50'
    },
    'ma_type': {
        'type': 'str',
        'default': 'ema',
        'options': ['sma', 'ema'],
        'description': 'Moving average type',
        'gui_hint': 'EMA reacts faster than SMA to recent price changes'
    }
}

# EXACT Test Function (DO NOT CHANGE)
def simple_test():
    """Test strategy - EXACT function required"""
    print("🧪 MY STRATEGY TEST")
    print("=" * 30)
    
    try:
        # EXACT Test Call (DO NOT CHANGE)
        strategy = create_strategy(
            symbols=['ADAUSDT'],
            timeframes=['5m'],
            fast_period=20,
            slow_period=50,
            ma_type='ema'
        )
        
        print(f"✅ Strategy created: {strategy.name}")
        print(f"   Symbols: {strategy.symbols}")
        print(f"   Timeframes: {strategy.timeframes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# EXACT Main Execution (DO NOT CHANGE)
if __name__ == "__main__":
    simple_test()
 
 
 
EXACT Available Indicators (Copy-Paste Ready) 
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
16
17
18
19
20
21
# EXACT Indicator Functions (use exactly as shown)

# Moving Averages
sma(data, period=20)           # Simple Moving Average
ema(data, period=20)           # Exponential Moving Average
wma(data, period=20)           # Weighted Moving Average
dema(data, period=20)          # Double Exponential Moving Average
tema(data, period=20)          # Triple Exponential Moving Average

# Momentum
rsi(data, period=14)           # Relative Strength Index
stochastic(high, low, close, k_period=14, d_period=3)  # Stochastic Oscillator
srsi(data, period=14)          # Stochastic RSI
macd(data, fast_period=12, slow_period=26, signal_period=9)  # MACD
cci(high, low, close, period=20)  # Commodity Channel Index
atr(high, low, close, period=14)  # Average True Range
williams_r(high, low, close, period=14)  # Williams %R

# Volume (if available)
ad(high, low, close, volume)  # Accumulation/Distribution
obv(close, volume)           # On-Balance Volume
 
 
 
EXACT Available Signals (Copy-Paste Ready) 
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
16
17
# EXACT Signal Functions (use exactly as shown)

# Basic Signals
ma_crossover(fast_ma, slow_ma)                    # Moving Average Crossover
overbought_oversold(indicator, overbought=70, oversold=30)  # Overbought/Oversold

# Advanced Signals  
macd_signals(macd_line, signal_line, histogram=None)  # MACD Signals
bollinger_bands_signals(price, upper_band, lower_band, middle_band=None)  # Bollinger Bands
stochastic_signals(k_percent, d_percent, overbought=80, oversold=20)  # Stochastic Signals
divergence_signals(price, indicator, lookback_period=20)  # Divergence Signals
breakout_signals(price, resistance, support, penetration_pct=0.01)  # Breakout Signals
trend_strength_signals(price, short_ma, long_ma, adx=None, adx_threshold=25)  # Trend Strength

# Combination Signals
majority_vote_signals(signal_list)  # Majority Vote Combination
weighted_signals(signal_list)       # Weighted Combination
 
 
 
EXACT Strategy Examples (Copy-Paste Ready) 
Example 1: RSI Strategy 
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
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
# EXACT RSI Strategy
def create_strategy(symbols=None, timeframes=None, **params):
    # EXACT Parameter Handling
    if symbols is None or len(symbols) == 0:
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['1m']
    
    # EXACT Parameter Extraction
    rsi_period = params.get('rsi_period', 14)
    overbought = params.get('overbought', 70)
    oversold = params.get('oversold', 30)
    
    try:
        # EXACT StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # EXACT RSI Indicator
        strategy_builder.add_indicator('rsi', rsi, period=rsi_period)
        
        # EXACT RSI Signal
        strategy_builder.add_signal_rule('rsi_signal', overbought_oversold,
                                       indicator='rsi',
                                       overbought=overbought,
                                       oversold=oversold)
        
        # EXACT Setup
        strategy_builder.set_signal_combination('majority_vote')
        strategy_builder.set_strategy_info('RSI_Strategy', '1.0.0')
        
        return strategy_builder.build()
        
    except Exception as e:
        logger.error(f"❌ Error creating strategy: {e}")
        raise

# EXACT Parameters
STRATEGY_PARAMETERS = {
    'rsi_period': {
        'type': 'int',
        'default': 14,
        'min': 5,
        'max': 50,
        'description': 'RSI calculation period',
        'gui_hint': 'Standard: 14, Shorter: 5-10, Longer: 20-30'
    },
    'overbought': {
        'type': 'int',
        'default': 70,
        'min': 50,
        'max': 90,
        'description': 'RSI overbought level',
        'gui_hint': 'Standard: 70, More sensitive: 75-80'
    },
    'oversold': {
        'type': 'int',
        'default': 30,
        'min': 10,
        'max': 50,
        'description': 'RSI oversold level',
        'gui_hint': 'Standard: 30, More sensitive: 20-25'
    }
}
 
 
 
Example 2: MACD Strategy 
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
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
⌄
# EXACT MACD Strategy
def create_strategy(symbols=None, timeframes=None, **params):
    # EXACT Parameter Handling
    if symbols is None or len(symbols) == 0:
        symbols = ['BTCUSDT']
    
    if timeframes is None or len(timeframes) == 0:
        timeframes = ['1m']
    
    # EXACT Parameter Extraction
    fast_period = params.get('fast_period', 12)
    slow_period = params.get('slow_period', 26)
    signal_period = params.get('signal_period', 9)
    
    try:
        # EXACT StrategyBuilder
        strategy_builder = StrategyBuilder(symbols, timeframes)
        
        # EXACT MACD Indicator
        strategy_builder.add_indicator('macd', macd, 
                                     fast_period=fast_period,
                                     slow_period=slow_period,
                                     signal_period=signal_period)
        
        # EXACT MACD Signal
        strategy_builder.add_signal_rule('macd_signal', macd_signals,
                                       macd_line='macd_macd_line',
                                       signal_line='macd_signal_line')
        
        # EXACT Setup
        strategy_builder.set_signal_combination('majority_vote')
        strategy_builder.set_strategy_info('MACD_Strategy', '1.0.0')
        
        return strategy_builder.build()
        
    except Exception as e:
        logger.error(f"❌ Error creating strategy: {e}")
        raise

# EXACT Parameters
STRATEGY_PARAMETERS = {
    'fast_period': {
        'type': 'int',
        'default': 12,
        'min': 5,
        'max': 50,
        'description': 'MACD fast EMA period',
        'gui_hint': 'Standard: 12, Shorter: 5-10, Longer: 15-20'
    },
    'slow_period': {
        'type': 'int',
        'default': 26,
        'min': 15,
        'max': 100,
        'description': 'MACD slow EMA period',
        'gui_hint': 'Standard: 26, Shorter: 20-25, Longer: 30-50'
    },
    'signal_period': {
        'type': 'int',
        'default': 9,
        'min': 5,
        'max': 20,
        'description': 'MACD signal line period',
        'gui_hint': 'Standard: 9, Shorter: 5-8, Longer: 10-15'
    }
}
 
 
 
EXACT Testing Instructions 
Step 1: Create File 
bash
 
 
 
1
2
3
# EXACT File Location
cd AIAssistedTradeBot/simple_strategy/strategies/
touch My_Strategy.py
 
 
 
Step 2: Copy Template 
bash
 
 
 
1
2
# Copy the EXACT template above
# Paste it into My_Strategy.py
 
 
 
Step 3: Test Strategy 
bash
 
 
 
1
2
3
# EXACT Test Command
cd AIAssistedTradeBot/
python -c "from simple_strategy.strategies.My_Strategy import simple_test; simple_test()"
 
 
 
Step 4: GUI Test 
bash
 
 
 
1
2
3
4
5
6
7
8
9
# EXACT GUI Test
1. Run: python main.py
2. Open backtest window
3. Select "My_Strategy" from dropdown
4. Choose symbol: ADAUSDT
5. Choose timeframe: 5m
6. Set parameters (use defaults)
7. Click "Create Strategy"
8. Click "Run Backtest"
 
 
 
EXACT Success Criteria 
The strategy works if you see:
```
🧪 MY STRATEGY TEST 

✅ Strategy created: My_Strategy
   Symbols: ['ADAUSDT']
   Timeframes: ['5m'] 
 
 
 
1
2

And in GUI backtest:
 
 
 

🔧 Creating strategy with: 

     Symbols: ['ADAUSDT']
     Timeframes: ['5m']
     Fast Period: 20
     Slow Period: 50
    ✅ Strategy created successfully!
     

 
 
 
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
26
27
28
29
30
31
32
33
34

## EXACT Error Solutions

### Error: "No module named 'simple_strategy'"
**Solution**: File is in wrong location, must be in `simple_strategy/strategies/`

### Error: "Strategy not appearing in GUI"
**Solution**: Missing `create_strategy` function or `STRATEGY_PARAMETERS` dictionary

### Error: "0 trades generated"
**Solution**: Check symbol/timeframe handling in `create_strategy` function

### Error: "Import error"
**Solution**: Use EXACT imports provided in template

---

## **100% GUARANTEE**

If you provide this **exact documentation** to any AI and ask:

> "Create a [specific type] strategy for my AIAssistedTradeBot project using this exact template and following all EXACT instructions"

The AI should create a working strategy on the first try because:

1. ✅ **Exact file structure** is specified
2. ✅ **Exact imports** are provided
3. ✅ **Exact function signatures** are specified
4. ✅ **Exact API usage** is shown
5. ✅ **Exact parameter handling** is demonstrated
6. ✅ **Exact testing procedure** is provided
7. ✅ **Exact error solutions** are included

This removes all guesswork and should work with any competent AI assistant.
