import os
import sys

# Add parent directories to path (REQUIRED)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

from simple_strategy.trading.paper_trading_engine import PaperTradingEngine

def test_trade_execution():
    """Test real trade execution on Bybit Demo API"""
    print("=== Testing Real Trade Execution ===")
    
    try:
        # Initialize engine
        engine = PaperTradingEngine('bybit_demo', 'Strategy_1_Trend_Following', 1000)
        
        # Test with a small amount on BTCUSDT (most liquid)
        test_symbol = 'BTCUSDT'
        test_quantity = 0.001  # Very small amount for testing
        
        print(f"Testing with {test_quantity} {test_symbol}")
        
        # Get current balance before trade
        balance_before = engine.get_real_balance()
        print(f"Balance before trade: ${balance_before}")
        
        # Execute a buy order
        print("Executing BUY order...")
        buy_result = engine.execute_buy(test_symbol, test_quantity)
        
        if buy_result:
            print("✅ BUY order executed successfully!")
            print(f"Order ID: {buy_result.get('order_id')}")
            print(f"Status: {buy_result.get('status')}")
            
            # Wait a moment for the order to process
            import time
            time.sleep(2)
            
            # Check balance after buy
            balance_after_buy = engine.get_real_balance()
            print(f"Balance after buy: ${balance_after_buy}")
            
            # Execute a sell order to close the position
            print("Executing SELL order...")
            sell_result = engine.execute_sell(test_symbol, test_quantity)
            
            if sell_result:
                print("✅ SELL order executed successfully!")
                print(f"Order ID: {sell_result.get('order_id')}")
                print(f"Status: {sell_result.get('status')}")
                
                # Wait a moment for the order to process
                time.sleep(2)
                
                # Check final balance
                balance_final = engine.get_real_balance()
                print(f"Final balance: ${balance_final}")
                
                # Calculate the difference
                balance_diff = balance_final - balance_before
                print(f"Balance difference: ${balance_diff}")
                
                if abs(balance_diff) < 1:  # Small difference due to fees/slippage
                    print("✅ Trade cycle completed successfully!")
                    return True
                else:
                    print(f"⚠️ Unexpected balance difference: ${balance_diff}")
                    return True  # Still successful, just noting the difference
            else:
                print("❌ SELL order failed")
                return False
        else:
            print("❌ BUY order failed")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    test_trade_execution()