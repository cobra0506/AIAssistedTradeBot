import os
import sys

# Add parent directories to path (REQUIRED)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

from simple_strategy.trading.paper_trading_engine import PaperTradingEngine

def test_paper_trading_engine():
    """Test the updated paper trading engine with Direct HTTP"""
    print("=== Testing Paper Trading Engine (Direct HTTP) ===")
    
    try:
        # Initialize engine
        engine = PaperTradingEngine('bybit_demo', 'Strategy_1_Trend_Following', 1000)
        
        # Test connection
        if engine.api_key and engine.api_secret:
            print("✅ API credentials loaded successfully")
        else:
            print("❌ Failed to load API credentials")
            return False
        
        # Test balance fetch
        balance = engine.get_balance()
        if balance > 0:
            print(f"✅ Balance fetch successful: ${balance}")
        else:
            print("❌ Failed to fetch balance")
            return False
        
        # Test symbol fetch
        symbols = engine.get_all_perpetual_symbols()
        if len(symbols) > 0:
            print(f"✅ Symbol fetch successful: {len(symbols)} symbols found")
            print(f"First 5 symbols: {symbols[:5]}")
        else:
            print("❌ Failed to fetch symbols")
            return False
        
        print("\n=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    test_paper_trading_engine()