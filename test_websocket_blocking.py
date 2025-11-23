import asyncio
import time
import sys
import os
import logging

# Add the project root to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from shared_modules.data_collection.config import DataCollectionConfig
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.logging_utils import setup_logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

async def test_websocket_blocking():
    """Test to confirm WebSocket is blocking historical data fetch"""
    print("\n" + "="*60)
    print("TESTING: WebSocket Blocking Behavior")
    print("="*60)
    
    # Create config with WebSocket enabled
    config = DataCollectionConfig()
    config.ENABLE_WEBSOCKET = True  # Make sure WebSocket is enabled
    config.LIMIT_TO_50_ENTRIES = True  # Use limited data for faster testing
    config.DAYS_TO_FETCH = 1  # Just 1 day for faster testing
    
    # Create hybrid system
    hybrid_system = HybridTradingSystem(config)
    await hybrid_system.initialize()
    
    # Test 1: Check if WebSocket setup returns
    print("\n[TEST] Testing WebSocket setup...")
    start_time = time.time()
    
    if config.ENABLE_WEBSOCKET and hybrid_system.websocket_handler:
        print("[TEST] WebSocket enabled, testing connection...")
        # This should hang if our diagnosis is correct
        try:
            # Wait max 5 seconds for WebSocket setup to complete
            await asyncio.wait_for(hybrid_system.websocket_handler.connect(), timeout=5.0)
            elapsed = time.time() - start_time
            print(f"[TEST] WebSocket setup completed in {elapsed:.2f} seconds")
            is_blocking = False
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            print(f"[TEST] CONFIRMED: WebSocket setup is blocking (timeout after {elapsed:.2f} seconds)")
            is_blocking = True
    else:
        print("[TEST] WebSocket disabled, cannot test blocking behavior")
        is_blocking = False
    
    # Test 2: Try to fetch historical data after WebSocket setup
    print("\n[TEST] Testing historical data fetch after WebSocket setup...")
    start_time = time.time()
    
    try:
        # Wait max 5 seconds for historical data fetch to start
        await asyncio.wait_for(
            hybrid_system.fetch_data_hybrid(mode="recent"), 
            timeout=5.0
        )
        elapsed = time.time() - start_time
        print(f"[TEST] Historical data fetch started in {elapsed:.2f} seconds")
        hist_data_started = True
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"[TEST] CONFIRMED: Historical data fetch is blocked (timeout after {elapsed:.2f} seconds)")
        hist_data_started = False
    
    # Cleanup
    print("\n[TEST] Cleaning up...")
    if hasattr(hybrid_system, 'shared_ws_manager'):
        await hybrid_system.shared_ws_manager.shutdown()
    
    # Print results
    print("\n" + "="*60)
    print("TEST RESULTS:")
    print("="*60)
    
    if is_blocking:
        print("❌ WebSocket IS BLOCKING")
        print("   - WebSocket setup does not return")
        print("   - This prevents historical data from being fetched")
    else:
        print("✅ WebSocket is NOT blocking")
        print("   - WebSocket setup completes and returns")
    
    if not hist_data_started:
        print("❌ Historical data fetch IS BLOCKED")
        print("   - Cannot start fetching historical data")
    else:
        print("✅ Historical data fetch is NOT blocked")
        print("   - Historical data fetching started successfully")
    
    print("\n" + "="*60)
    
    if is_blocking or not hist_data_started:
        print("CONCLUSION: The WebSocket is blocking historical data fetching.")
        print("ACTION NEEDED: Implement the non-blocking WebSocket fix.")
    else:
        print("CONCLUSION: No blocking issues detected.")
        print("The system appears to be working correctly.")
    
    print("="*60)
    
    return is_blocking or not hist_data_started

async def test_without_websocket():
    """Test the system with WebSocket disabled for comparison"""
    print("\n" + "="*60)
    print("TESTING: System with WebSocket DISABLED")
    print("="*60)
    
    # Create config with WebSocket disabled
    config = DataCollectionConfig()
    config.ENABLE_WEBSOCKET = False  # Disable WebSocket
    config.LIMIT_TO_50_ENTRIES = True  # Use limited data for faster testing
    config.DAYS_TO_FETCH = 1  # Just 1 day for faster testing
    
    # Create hybrid system
    hybrid_system = HybridTradingSystem(config)
    await hybrid_system.initialize()
    
    # Test historical data fetch
    print("\n[TEST] Testing historical data fetch without WebSocket...")
    start_time = time.time()
    
    try:
        # Wait max 10 seconds for historical data fetch to complete
        result = await asyncio.wait_for(
            hybrid_system.fetch_data_hybrid(mode="recent"), 
            timeout=10.0
        )
        elapsed = time.time() - start_time
        print(f"[TEST] Historical data fetch completed in {elapsed:.2f} seconds")
        success = True
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"[TEST] Historical data fetch timed out after {elapsed:.2f} seconds")
        success = False
    
    # Cleanup
    print("\n[TEST] Cleaning up...")
    if hasattr(hybrid_system, 'shared_ws_manager'):
        await hybrid_system.shared_ws_manager.shutdown()
    
    # Print results
    print("\n" + "="*60)
    print("TEST RESULTS (WebSocket Disabled):")
    print("="*60)
    
    if success:
        print("✅ Historical data fetch completed successfully")
        print("   - System works correctly when WebSocket is disabled")
    else:
        print("❌ Historical data fetch failed")
        print("   - There may be other issues beyond WebSocket blocking")
    
    print("="*60)
    
    return success

async def main():
    """Main test function"""
    print("AI Assisted TradeBot - WebSocket Blocking Test")
    print("This test will verify if WebSocket is blocking historical data fetching")
    
    # Test 1: With WebSocket enabled
    blocking_detected = await test_websocket_blocking()
    
    # Test 2: With WebSocket disabled (for comparison)
    websocket_disabled_works = await test_without_websocket()
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    
    if blocking_detected:
        if websocket_disabled_works:
            print("✅ CONFIRMED: WebSocket is the cause of the blocking issue")
            print("   - System works when WebSocket is disabled")
            print("   - System fails when WebSocket is enabled")
            print("\nRECOMMENDATION: Implement the non-blocking WebSocket fix")
        else:
            print("⚠️  Multiple issues detected")
            print("   - WebSocket is blocking")
            print("   - Historical data fetch fails even without WebSocket")
            print("\nRECOMMENDATION: Fix both WebSocket blocking and historical data issues")
    else:
        print("✅ No WebSocket blocking detected")
        print("   - System appears to be working correctly")
    
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())