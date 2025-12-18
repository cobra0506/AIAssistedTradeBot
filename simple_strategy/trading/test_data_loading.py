import os
import sys
import pandas as pd
import numpy as np
import traceback
from datetime import datetime

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def calculate_rsi(prices, period=14):
    """Calculate RSI directly in this test file"""
    try:
        if len(prices) < period + 1:
            return np.array([50.0] * len(prices))  # Default to neutral
        
        # Calculate price changes
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - (100./(1.+rs))
        
        # Calculate the rest of RSI values
        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up/down
            rsi[i] = 100. - (100./(1.+rs))
        
        return rsi
    except Exception as e:
        print(f"❌ Error calculating RSI: {e}")
        traceback.print_exc()
        return np.array([50.0] * len(prices))  # Default to neutral

class SimpleRSIStrategy:
    """A simple RSI strategy that we know works"""
    def __init__(self, rsi_period=14, rsi_overbought=70, rsi_oversold=30):
        self.rsi_period = rsi_period
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold
        
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return np.array([50.0] * len(prices))  # Default to neutral
        
        # Calculate price changes
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - (100./(1.+rs))
        
        # Calculate the rest of RSI values
        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            
            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up/down
            rsi[i] = 100. - (100./(1.+rs))
        
        return rsi
        
    def generate_signals(self, df):
        """Generate trading signals based on RSI"""
        if df is None or len(df) < self.rsi_period + 1:
            return pd.DataFrame({'signal': [0] * len(df)})
        
        closes = df['close'].values
        rsi_values = self.calculate_rsi(closes, period=self.rsi_period)
        
        # Generate signals
        signals = []
        for i in range(len(df)):
            if i < self.rsi_period:
                signals.append(0)  # No signal until we have enough data
            else:
                current_rsi = rsi_values[i]
                if current_rsi < self.rsi_oversold:
                    signals.append(1)  # Buy signal
                elif current_rsi > self.rsi_overbought:
                    signals.append(-1)  # Sell signal
                else:
                    signals.append(0)  # Hold signal
        
        return pd.DataFrame({'signal': signals})

def test_existing_strategy_file():
    """Test an existing strategy file"""
    print("\n=== Testing Existing Strategy File ===")
    
    strategies_dir = os.path.join(project_root, 'simple_strategy', 'strategies')
    
    # Check the content of the RSI strategy file
    rsi_strategy_path = os.path.join(strategies_dir, 'Strategy_Simple_RSI_Extremes.py')
    if os.path.exists(rsi_strategy_path):
        print(f"\n--- RSI Strategy File Content ---")
        try:
            with open(rsi_strategy_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(content)
        except UnicodeDecodeError:
            try:
                with open(rsi_strategy_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                    print(content)
            except Exception as e:
                print(f"❌ Could not read file: {e}")
    else:
        print(f"❌ RSI Strategy file not found at {rsi_strategy_path}")

def test_paper_trader_logic():
    """Test the paper trader logic without importing it"""
    print("\n=== Testing Paper Trader Logic ===")
    
    # Simulate the paper trader's generate_strategy_signal method
    def generate_strategy_signal(symbol, strategy):
        """Generate signal using the loaded strategy"""
        try:
            # Get historical data for the symbol
            csv_file = os.path.join(project_root, 'data', f'{symbol}_1.csv')
            df = pd.read_csv(csv_file)
            if 'timestamp' in df.columns and 'datetime' not in df.columns:
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('datetime')
            
            # Explicitly check for None or empty DataFrame
            if df is None:
                print(f"⚠️ No historical data available for {symbol}")
                return 'HOLD'
            
            if isinstance(df, pd.DataFrame) and df.empty:
                print(f"⚠️ Empty historical data for {symbol}")
                return 'HOLD'
            
            if len(df) < 50:
                print(f"⚠️ Not enough historical data for {symbol} (only {len(df)} rows)")
                return 'HOLD'
            
            # Generate signals using the strategy
            signals = strategy.generate_signals(df)
            
            # Get the latest signal
            if signals is not None and len(signals) > 0:
                if isinstance(signals, pd.DataFrame):
                    latest_signal = signals.iloc[-1]['signal']
                elif isinstance(signals, dict) and 'signal' in signals:
                    latest_signal = signals['signal']
                else:
                    latest_signal = signals[-1] if isinstance(signals, (list, np.ndarray)) else 0
                
                # Convert signal to string
                if latest_signal == 1:
                    return 'BUY'
                elif latest_signal == -1:
                    return 'SELL'
                else:
                    return 'HOLD'
            
            return 'HOLD'
            
        except Exception as e:
            print(f"❌ Error generating strategy signal for {symbol}: {e}")
            traceback.print_exc()
            return 'HOLD'
    
    # Create our simple strategy
    strategy = SimpleRSIStrategy(rsi_period=14, rsi_overbought=70, rsi_oversold=30)
    
    # Test with a few symbols
    test_symbols = ['BTCUSDT', 'ETHUSDT', 'YFIUSDT', 'YGGUSDT']
    for symbol in test_symbols:
        print(f"\n--- Testing {symbol} ---")
        signal = generate_strategy_signal(symbol, strategy)
        print(f"Signal for {symbol}: {signal}")

def test_error_reproduction():
    """Try to reproduce the exact error from the paper trader"""
    print("\n=== Reproducing Paper Trader Error ===")
    
    # The error message was "1766004060000" which is a timestamp
    # Let's see if we can reproduce this by passing the wrong type to generate_signals
    
    strategy = SimpleRSIStrategy(rsi_period=14, rsi_overbought=70, rsi_oversold=30)
    
    # Test 1: Pass a timestamp instead of a DataFrame
    print("\n--- Test 1: Passing timestamp instead of DataFrame ---")
    try:
        timestamp = 1766004060000
        signals = strategy.generate_signals(timestamp)
        print(f"❌ Expected error but got: {signals}")
    except Exception as e:
        print(f"✅ Got expected error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 2: Pass None
    print("\n--- Test 2: Passing None ---")
    try:
        signals = strategy.generate_signals(None)
        print(f"❌ Expected error but got: {signals}")
    except Exception as e:
        print(f"✅ Got expected error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 3: Pass an empty DataFrame
    print("\n--- Test 3: Passing empty DataFrame ---")
    try:
        df = pd.DataFrame()
        signals = strategy.generate_signals(df)
        print(f"Result: {signals}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 4: Pass a DataFrame with insufficient data
    print("\n--- Test 4: Passing DataFrame with insufficient data ---")
    try:
        df = pd.DataFrame({'close': [100.0, 101.0, 102.0]})
        signals = strategy.generate_signals(df)
        print(f"Result: {signals}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_existing_strategy_file()
    test_paper_trader_logic()
    test_error_reproduction()