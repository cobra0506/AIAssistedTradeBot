# Test to debug signal generation and position sizing
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

def test_signal_generation():
    """Test if signals are being generated correctly"""
    print("=== DEBUG: Signal Generation Test ===")
    
    try:
        # Import required modules
        from simple_strategy.strategies.Strategy_Simple_Test import create_strategy
        from simple_strategy.shared.data_feeder import DataFeeder
        import pandas as pd
        
        # Create strategy
        strategy = create_strategy(['SOLUSDT'], ['1m'])
        print(f"✅ Strategy created: {strategy.get_strategy_info()['strategy_name']}")
        
        # Load data
        feeder = DataFeeder(data_dir='data')
        data = feeder._load_csv_file('SOLUSDT', '1m')
        
        if data is None:
            print("❌ Failed to load data")
            return
        
        print(f"✅ Data loaded: {len(data)} rows")
        print(f"📊 Date range: {data.index.min()} to {data.index.max()}")
        print(f"📊 Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        
        # Test signal generation on a small sample
        sample_data = data.tail(100)  # Last 100 rows
        print(f"📊 Testing with sample of {len(sample_data)} rows")
        
        # Prepare data for strategy
        strategy_data = {'SOLUSDT': {'1m': sample_data}}
        
        # Generate signals
        signals = strategy.generate_signals(strategy_data)
        print(f"📊 Generated signals: {signals}")
        
        # Check if any signals are not HOLD
        for symbol, timeframes in signals.items():
            for timeframe, signal in timeframes.items():
                print(f"📊 {symbol} {timeframe} signal: {signal}")
                if signal != 'HOLD':
                    print(f"✅ Found non-HOLD signal: {signal}")
                    
                    # Test position sizing
                    current_price = sample_data['close'].iloc[-1]
                    position_size = strategy.calculate_position_size(
                        symbol='SOLUSDT',
                        current_price=current_price,
                        signal=signal,
                        account_balance=10000.0
                    )
                    print(f"📊 Position size for {signal} at ${current_price:.2f}: {position_size}")
                    
                    if position_size > 0:
                        print(f"✅ Valid position size: {position_size}")
                    else:
                        print(f"❌ Invalid position size: {position_size}")
                else:
                    print("⚠️ Signal is HOLD")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_signal_generation()