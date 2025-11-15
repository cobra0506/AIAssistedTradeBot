import os
import sys

# Add parent directories to path (REQUIRED)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

from simple_strategy.trading.paper_trading_engine import PaperTradingEngine

def test_symbol_fetching():
    """Test just the symbol fetching functionality"""
    print("=== Testing Symbol Fetching ===")
    
    try:
        # Initialize engine
        engine = PaperTradingEngine('bybit_demo', 'Strategy_1_Trend_Following', 1000)
        
        # Test symbol fetch
        symbols = engine.get_all_perpetual_symbols()
        
        if len(symbols) > 0:
            print(f"✅ SUCCESS: Found {len(symbols)} symbols")
            print(f"First 10 symbols: {symbols[:10]}")
            print(f"Last 10 symbols: {symbols[-10:]}")
            return True
        else:
            print("❌ FAILED: No symbols found")
            return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    test_symbol_fetching()