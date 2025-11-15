import os
import sys
import time

# Add parent directories to path (REQUIRED)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

from simple_working_engine import SimpleWorkingEngine

def test_simple_engine():
    """Test the simple working engine"""
    print("=== Testing Simple Working Engine ===")
    
    try:
        # Initialize engine
        engine = SimpleWorkingEngine('bybit_demo', 'Strategy_1_Trend_Following', 1000)
        
        # Test 1: Get balance
        print("\n--- Test 1: Get Balance ---")
        balance = engine.get_balance()
        print(f"Current balance: ${balance}")
        
        # Test 2: Get symbols
        print("\n--- Test 2: Get Symbols ---")
        symbols = engine.get_symbols()
        print(f"Found {len(symbols)} symbols")
        if symbols:
            print(f"First 5: {symbols[:5]}")
        
        # Test 3: Execute trade cycle
        print("\n--- Test 3: Trade Cycle ---")
        test_symbol = 'BTCUSDT'
        test_quantity = 0.001
        
        balance_before = balance
        print(f"Balance before: ${balance_before}")
        
        # Buy
        buy_result = engine.execute_buy(test_symbol, test_quantity)
        if buy_result:
            time.sleep(2)  # Wait for order to process
            
            # Get balance after buy
            balance_after_buy = engine.get_balance()
            print(f"Balance after buy: ${balance_after_buy}")
            
            # Sell
            sell_result = engine.execute_sell(test_symbol, test_quantity)
            if sell_result:
                time.sleep(2)  # Wait for order to process
                
                # Get final balance
                balance_final = engine.get_balance()
                print(f"Final balance: ${balance_final}")
                
                # Calculate difference
                diff = balance_final - balance_before
                print(f"Balance difference: ${diff}")
                
                if abs(diff) < 1:  # Small difference due to fees
                    print("✅ Trade cycle completed successfully!")
                    return True
                else:
                    print(f"⚠️ Balance difference: ${diff}")
                    return True
            else:
                print("❌ Sell order failed")
                return False
        else:
            print("❌ Buy order failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    test_simple_engine()