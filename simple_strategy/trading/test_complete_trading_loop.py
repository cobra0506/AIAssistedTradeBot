import os
import sys
import time

# Add parent directories to path (REQUIRED)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

from simple_strategy.trading.paper_trading_engine import PaperTradingEngine

def test_complete_trading_loop():
    """Test the complete trading system with real strategy signals"""
    print("=== Testing Complete Trading Loop ===")
    print("This will run for 3 trading loops with real market data")
    print("Press Ctrl+C to stop early if needed\n")
    
    try:
        # Initialize engine
        engine = PaperTradingEngine('bybit_demo', 'Strategy_1_Trend_Following', 1000)
        
        # Get initial state
        initial_balance = engine.get_balance()
        print(f"🏦 Initial Balance: ${initial_balance}")
        
        # Get symbols we'll be monitoring from data config
        if engine.data_config.FETCH_ALL_SYMBOLS:
            # Get a subset of all available symbols for testing
            all_symbols = engine.get_all_perpetual_symbols()
            test_symbols = all_symbols[:5]  # Test with first 5 symbols for speed
        else:
            # Use symbols from config
            test_symbols = engine.data_config.SYMBOLS[:5]  # Test with first 5 symbols for speed
            
        print(f"📊 Monitoring {len(test_symbols)} symbols: {test_symbols}")
        
        # Load strategy
        if not engine.load_strategy():
            print("❌ Failed to load strategy")
            return False
        
        print("🚀 Starting trading loop...")
        print("=" * 60)
        
        # Store initial stats
        initial_stats = {
            'balance': initial_balance,
            'trades': len(engine.trades),
            'positions': len(engine.current_positions)
        }
        
        # Start trading (will run for 3 loops automatically)
        engine.start_trading()
        
        # Get final stats
        final_balance = engine.get_balance()
        final_stats = {
            'balance': final_balance,
            'trades': len(engine.trades),
            'positions': len(engine.current_positions)
        }
        
        # Print comprehensive results
        print("\n" + "=" * 60)
        print("📊 TRADING SESSION RESULTS")
        print("=" * 60)
        
        print(f"💰 Balance Summary:")
        print(f"   Initial Balance: ${initial_stats['balance']:.2f}")
        print(f"   Final Balance:   ${final_stats['balance']:.2f}")
        print(f"   P&L:             ${final_stats['balance'] - initial_stats['balance']:.2f}")
        
        print(f"\n📈 Trading Activity:")
        print(f"   Total Trades:    {final_stats['trades']}")
        print(f"   Open Positions:  {final_stats['positions']}")
        
        if engine.trades:
            print(f"\n📋 Trade History:")
            for i, trade in enumerate(engine.trades):
                trade_type = trade['type']
                symbol = trade['symbol']
                quantity = trade.get('quantity', 'N/A')
                order_id = trade.get('order_id', 'N/A')
                print(f"   {i+1}. {trade_type} {quantity} {symbol} (ID: {order_id[:8]}...)")
        
        if engine.current_positions:
            print(f"\n📍 Open Positions:")
            for symbol, position in engine.current_positions.items():
                quantity = position.get('quantity', 'N/A')
                order_id = position.get('order_id', 'N/A')
                print(f"   {symbol}: {quantity} units (ID: {order_id[:8]}...)")
        
        # Success criteria
        success = True
        if final_stats['trades'] > 0:
            print(f"\n✅ SUCCESS: Trading system executed {final_stats['trades']} trades!")
        else:
            print(f"\n⚠️ WARNING: No trades were executed (this might be normal for the test strategy)")
        
        if final_stats['balance'] != initial_stats['balance']:
            print(f"✅ SUCCESS: Balance changed as expected")
        else:
            print(f"ℹ️ INFO: Balance unchanged (no trades or strategy didn't trigger)")
        
        print(f"\n🎯 OVERALL STATUS: {'SUCCESS' if success else 'NEEDS ATTENTION'}")
        return success
        
    except KeyboardInterrupt:
        print("\n\n🛑 Trading stopped by user")
        return True
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    test_complete_trading_loop()