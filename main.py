# main.py - Updated with more frequent CSV updates
import os
import csv
import asyncio
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from config import DataCollectionConfig
from hybrid_system import HybridTradingSystem
from data_integrity import DataIntegrityChecker  # Keep if you want integrity checks

# Global configuration
config = DataCollectionConfig()

def debug_websocket_message(message: str):
    """Debug callback to see all WebSocket messages"""
    try:
        data = json.loads(message)
        if "topic" in data:
            print(f"🔍 Debug: Received message for topic: {data['topic']}")
        elif data.get("op") == "subscribe":
            print(f"🔍 Debug: Subscription response: {data}")
    except:
        pass  # Ignore JSON parsing errors for binary data

async def main():
    """Main function using the optimized hybrid system"""
    print("="*60)
    print("OPTIMIZED AI ASSISTED TRADING BOT")
    print("="*60)
    
    # Initialize the hybrid system
    hybrid_system = HybridTradingSystem(config)
    await hybrid_system.initialize()
    
    # Add debug callback to WebSocket
    if config.ENABLE_WEBSOCKET:
        hybrid_system.websocket_handler.add_debug_callback(debug_websocket_message)
    
    try:
        # Determine data collection mode
        if config.LIMIT_TO_50_ENTRIES:
            mode = "recent"
            print("📊 MODE: Recent 50 entries only")
        else:
            mode = "full"
            print("📊 MODE: Full historical data")
        
        if config.ENABLE_WEBSOCKET:
            print("📡 MODE: Live updates enabled")
        else:
            print("📡 MODE: Historical data only")
        
        # Get symbols to process
        if config.FETCH_ALL_SYMBOLS:
            print("🔍 Fetching all available symbols...")
            # This would be implemented in the hybrid system
            symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']  # Placeholder
        else:
            symbols = config.SYMBOLS
        
        print(f"📈 Processing {len(symbols)} symbols: {', '.join(symbols)}")
        print(f"⏰ Timeframes: {', '.join(config.TIMEFRAMES)}")
        
        # Fetch data with optimized system
        start_time = time.time()
        
        await hybrid_system.fetch_data_hybrid(
            symbols=symbols,
            timeframes=config.TIMEFRAMES,
            days=config.DAYS_TO_FETCH,
            mode=mode
        )
        
        # Performance reporting
        end_time = time.time()
        duration = end_time - start_time
        
        print("="*60)
        print("DATA COLLECTION COMPLETED")
        print("="*60)
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"📊 Mode: {mode}")
        print(f"📡 WebSocket: {'Enabled' if config.ENABLE_WEBSOCKET else 'Disabled'}")
        
        # Save data to CSV if needed
        if hasattr(hybrid_system, 'save_to_csv'):
            print("💾 Saving data to CSV files...")
            await hybrid_system.save_to_csv(config.DATA_DIR)
            print("✅ CSV files saved successfully")
        
        # Display final data status
        print("\n" + "="*60)
        print("FINAL DATA STATUS")
        print("="*60)
        
        for symbol in symbols:
            for timeframe in config.TIMEFRAMES:
                # Get historical data
                hist_data = hybrid_system.get_data(symbol, timeframe, "memory")
                # Get real-time data
                rt_data = hybrid_system.get_data(symbol, timeframe, "websocket")
                
                print(f"\n{symbol}_{timeframe}:")
                print(f"  Historical candles: {len(hist_data)}")
                print(f"  Real-time candles: {len(rt_data)}")
                
                if hist_data:
                    latest_hist = hist_data[-1]
                    dt = datetime.fromtimestamp(latest_hist['timestamp'] / 1000)
                    datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  Latest historical: {datetime_str}")
                
                if rt_data:
                    latest_rt = rt_data[-1]
                    dt = datetime.fromtimestamp(latest_rt['timestamp'] / 1000)
                    datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"  Latest real-time: {datetime_str}")
        
        # Run integrity check if enabled
        if config.RUN_INTEGRITY_CHECK:
            print("\n" + "="*60)
            print("RUNNING INTEGRITY CHECK")
            print("="*60)
            integrity_checker = DataIntegrityChecker(config)
            results = integrity_checker.check_all_files()
            print(f"Files checked: {results['files_checked']}")
            print(f"Files with issues: {results['files_with_issues']}")
            print(f"Total gaps: {results['total_gaps']}")
        
        # Keep running for live updates if WebSocket is enabled
        if config.ENABLE_WEBSOCKET:
            print("\n" + "="*60)
            print("LIVE UPDATES MODE - Press Ctrl+C to stop")
            print("="*60)
            print("⏰ CSV updates every 10 seconds")
            print("⏰ Status updates every 10 seconds")
            
            try:
                # Keep the program running for live updates
                live_update_count = 0
                last_csv_update = time.time()
                
                while True:
                    await asyncio.sleep(5)  # Check every 5 seconds instead of 10
                    live_update_count += 1
                    
                    current_time = time.time()
                    
                    # Update CSV files every 10 seconds (more frequent)
                    if current_time - last_csv_update >= 10:
                        print(f"\n📡 Live update #{live_update_count} at {datetime.now().strftime('%H:%M:%S')}:")
                        await hybrid_system.update_csv_with_realtime_data(config.DATA_DIR)
                        last_csv_update = current_time
                        
                        # Display current status
                        for symbol in symbols:
                            for timeframe in config.TIMEFRAMES:
                                rt_data = hybrid_system.get_data(symbol, timeframe, "websocket")
                                if rt_data:
                                    latest = rt_data[-1]
                                    dt = datetime.fromtimestamp(latest['timestamp'] / 1000)
                                    datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                                    print(f"  {symbol}_{timeframe}: {len(rt_data)} candles, latest: {datetime_str}")
                    
                    # Show brief status every 5 seconds (without CSV update)
                    else:
                        # Every other iteration (every 10 seconds) show a brief status
                        if live_update_count % 2 == 0:
                            print(f"⏰ Tick... {datetime.now().strftime('%H:%M:%S')} (WebSocket: {'Connected' if hybrid_system.websocket_handler.running else 'Disconnected'})")
                    
            except KeyboardInterrupt:
                print("\n🛑 Stopping live updates...")
        
        print("\n✅ Program completed successfully")
    
    finally:
        # Clean up resources
        await hybrid_system.close()

async def test_websocket_functionality():
    """Test WebSocket functionality with the hybrid system"""
    print("="*60)
    print("WEBSOCKET FUNCTIONALITY TEST")
    print("="*60)
    
    # Create test configuration
    test_config = DataCollectionConfig()
    test_config.SYMBOLS = ['BTCUSDT']
    test_config.TIMEFRAMES = ['1']
    test_config.DAYS_TO_FETCH = 1
    test_config.ENABLE_WEBSOCKET = True
    test_config.LIMIT_TO_50_ENTRIES = True
    
    # Initialize hybrid system
    hybrid_system = HybridTradingSystem(test_config)
    await hybrid_system.initialize()
    
    # Add debug callback to WebSocket
    hybrid_system.websocket_handler.add_debug_callback(debug_websocket_message)
    
    # Test results tracking
    test_results = {
        'candles_received': 0,
        'start_time': time.time(),
        'last_candle_time': None
    }
    
    def test_callback(symbol: str, timeframe: str, candle: Dict):
        """Test callback to track received candles"""
        test_results['candles_received'] += 1
        test_results['last_candle_time'] = candle['timestamp']
        print(f"📊 TEST: Received candle #{test_results['candles_received']} for {symbol}_{timeframe}")
        print(f"   Timestamp: {candle['timestamp']}")
        print(f"   Confirm: {candle.get('confirm', False)}")
    
    # Add callback to WebSocket handler
    hybrid_system.websocket_handler.add_callback(test_callback)
    
    # Start data collection
    await hybrid_system.fetch_data_hybrid(
        symbols=test_config.SYMBOLS,
        timeframes=test_config.TIMEFRAMES,
        days=test_config.DAYS_TO_FETCH,
        mode="live"
    )
    
    # Wait for test duration (2 minutes)
    print("🧪 Running test for 2 minutes...")
    await asyncio.sleep(120)
    
    # Print test results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Test duration: 120 seconds")
    print(f"Candles received: {test_results['candles_received']}")
    print(f"Last candle time: {test_results['last_candle_time']}")
    
    if test_results['candles_received'] > 0:
        print("✅ WebSocket test PASSED")
    else:
        print("❌ WebSocket test FAILED")

if __name__ == "__main__":
    # Check if running in test mode
    if config.TEST_WEBSOCKET:
        asyncio.run(test_websocket_functionality())
    else:
        asyncio.run(main())

'''import os
import csv
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from config import DataCollectionConfig
from data_fetcher import FastDataFetcher
from data_integrity import DataIntegrityChecker
from websocket_handler import WebSocketHandler

# Global lock for CSV file operations
csv_lock = asyncio.Lock()

async def update_csv_file(symbol: str, timeframe: str, new_candle: Dict):
    """Update CSV file with new completed candle"""
    filename = os.path.join(config.DATA_DIR, f"{symbol}_{timeframe}.csv")
    
    async with csv_lock:
        # Read existing data
        existing_data = []
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
        
        # Remove 'confirm' field from candle before saving to CSV
        candle_for_csv = {k: v for k, v in new_candle.items() if k != 'confirm'}
        
        # Check if candle already exists (avoid duplicates)
        existing_timestamps = {c['timestamp'] for c in existing_data}
        if candle_for_csv['timestamp'] not in existing_timestamps:
            # Add new candle
            existing_data.append(candle_for_csv)
            
            # Maintain 50-entry limit if configured
            if config.LIMIT_TO_50_ENTRIES and len(existing_data) > 50:
                existing_data = existing_data[-50:]
            
            # Write back to file
            with open(filename, 'w', newline='') as f:
                fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_data)
            
            print(f"✓ LIVE UPDATE: {symbol}_{timeframe} - New candle at {new_candle['timestamp']}")

def process_real_time_candle(symbol: str, timeframe: str, candle: Dict):
    """Callback function to process real-time candles"""
    if candle['confirm']:  # Only process completed candles
        print(f"🔥 Processing confirmed candle for {symbol}_{timeframe}")
        # Create a task to update the CSV file
        asyncio.create_task(update_csv_file(symbol, timeframe, candle))

def merge_historical_realtime(historical_data: List[Dict], realtime_data: List[Dict]) -> List[Dict]:
    """Merge historical and real-time data, avoiding duplicates"""
    if not historical_data:
        # Remove 'confirm' field from real-time data
        return [{k: v for k, v in candle.items() if k != 'confirm'} for candle in realtime_data]
    
    if not realtime_data:
        return historical_data
    
    # Get last timestamp in historical data
    last_historical_ts = historical_data[-1]['timestamp']
    
    # Filter real-time data to only include candles after historical
    new_data = [
        candle for candle in realtime_data
        if candle['timestamp'] > last_historical_ts
    ]
    
    # Remove 'confirm' field from new data
    new_data_clean = [{k: v for k, v in candle.items() if k != 'confirm'} for candle in new_data]
    
    return historical_data + new_data_clean

async def test_websocket_functionality():
    """Test WebSocket functionality to verify live data collection"""
    print("="*60)
    print("WEBSOCKET FUNCTIONALITY TEST")
    print("="*60)
    
    # Create test config with minimal settings
    test_config = DataCollectionConfig()
    test_config.SYMBOLS = ['BTCUSDT']
    test_config.TIMEFRAMES = ['1']
    test_config.DAYS_TO_FETCH = 1
    
    # Test data tracking
    test_results = {
        'candles_received': 0,
        'files_updated': 0,
        'start_time': time.time(),
        'last_candle_time': None,
        'messages_received': 0,
        'confirmed_candles': 0  # Track confirmed candles separately
    }
    
    def test_callback(symbol: str, timeframe: str, candle: Dict):
        """Test callback to track received candles"""
        test_results['candles_received'] += 1
        test_results['last_candle_time'] = candle['timestamp']
        print(f"📊 TEST: Received candle #{test_results['candles_received']} for {symbol}_{timeframe}")
        print(f"   Timestamp: {candle['timestamp']}")
        print(f"   Confirm: {candle['confirm']}")
    
    def debug_callback(message: str):
        """Debug callback to track all messages"""
        test_results['messages_received'] += 1
        
        # Print every 10th message to show activity
        if test_results['messages_received'] % 10 == 0:
            print(f"📡 Received message #{test_results['messages_received']}")
    
    # Start WebSocket
    print("Starting WebSocket for test...")
    ws_handler = WebSocketHandler(test_config)
    ws_handler.add_callback(test_callback)
    ws_handler.add_debug_callback(debug_callback)
    
    # Run WebSocket in background
    ws_task = asyncio.create_task(ws_handler.connect())
    
    # Wait for test duration (3 minutes for 1m candles)
    test_duration = 180  # 3 minutes
    print(f"Testing for {test_duration} seconds (3 minutes)...")
    
    try:
        # Show progress every 30 seconds
        for i in range(0, test_duration, 30):
            await asyncio.sleep(30)
            elapsed = time.time() - test_results['start_time']
            print(f"⏱️  Progress: {int(elapsed)}s / {test_duration}s - "
                  f"Messages: {test_results['messages_received']}, "
                  f"Candles: {test_results['candles_received']}")
    finally:
        # Stop WebSocket
        ws_handler.stop()
        # Wait a moment for the connection to close
        await asyncio.sleep(1)
        try:
            await ws_task
        except:
            pass  # Ignore errors when stopping
    
    # Print test results
    print("\n" + "="*60)
    print("TEST RESULTS")
    print("="*60)
    print(f"Test duration: {test_duration} seconds")
    print(f"Messages received: {test_results['messages_received']}")
    print(f"Candles received: {test_results['candles_received']}")
    print(f"Last candle time: {test_results['last_candle_time']}")
    
    # Check if test passed
    if test_results['candles_received'] > 0:
        print("✅ TEST PASSED: WebSocket is working correctly!")
        return True
    elif test_results['messages_received'] > 0:
        print("⚠️  TEST PARTIAL: Received messages but no completed candles.")
        print("This might be normal if no candles completed during the test.")
        return True  # Consider this a pass since we're receiving data
    else:
        print("❌ TEST FAILED: No messages received!")
        return False

async def run_data_collection():
    """Main data collection workflow"""
    global config
    
    print("="*60)
    print("FAST DATA COLLECTOR v3.0")
    print("="*60)
    
    # Create data directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Run WebSocket test if enabled
    if config.TEST_WEBSOCKET:
        test_passed = await test_websocket_functionality()
        if not test_passed:
            print("WebSocket test failed. Please check your connection and settings.")
            return
        print("\nContinuing with normal operation...\n")
    
    # Initialize variables
    ws_handler = None
    ws_task = None
    
    # First, determine which symbols to use
    print("Determining symbols to use...")
    if config.FETCH_ALL_SYMBOLS:
        print("Fetching all symbols from Bybit...")
        fetcher = FastDataFetcher(config)
        
        # Check if symbols were fetched successfully
        if not fetcher.all_symbols:
            print("Error: No symbols were fetched from Bybit. Using default symbols instead.")
            symbols_to_use = config.SYMBOLS
        else:
            symbols_to_use = fetcher.all_symbols
            print(f"Successfully fetched {len(symbols_to_use)} symbols from Bybit")
    else:
        symbols_to_use = config.SYMBOLS
        print(f"Using {len(symbols_to_use)} configured symbols")
    
    # Verify we have symbols to work with
    if not symbols_to_use:
        print("Error: No symbols available for data collection!")
        return
    
    # Now create and start WebSocket if enabled (after we know which symbols to use)
    if config.ENABLE_WEBSOCKET:
        print("Starting WebSocket connection...")
        ws_handler = WebSocketHandler(config, symbols_to_use)
        ws_handler.add_callback(process_real_time_candle)
        
        # Run WebSocket in background
        ws_task = asyncio.create_task(ws_handler.connect())
        
        # Wait for WebSocket to connect and complete subscriptions
        print("Waiting for WebSocket subscriptions to complete...")
        subscription_timeout = 30  # Maximum time to wait for subscriptions (seconds)
        start_time = time.time()
        
        while ws_task and not ws_task.done():
            await asyncio.sleep(1)
            elapsed = time.time() - start_time
            
            # Check if we've waited too long
            if elapsed > subscription_timeout:
                print(f"Warning: WebSocket subscription taking longer than {subscription_timeout} seconds. Continuing anyway.")
                break
            
            # Check if subscription count matches expected
            expected_subscriptions = len(symbols_to_use) * len(config.TIMEFRAMES)
            if ws_handler and hasattr(ws_handler, 'subscription_count'):
                progress = (ws_handler.subscription_count / expected_subscriptions) * 100
                print(f"Subscription progress: {ws_handler.subscription_count}/{expected_subscriptions} ({progress:.1f}%)")
                
                # If all subscriptions are complete, break the loop
                if ws_handler.subscription_count >= expected_subscriptions:
                    print("All WebSocket subscriptions completed!")
                    break
        
        print("WebSocket setup completed.")
    
    # Fetch historical data
    print("Fetching historical data...")
    fetcher = FastDataFetcher(config)
    
    # Create tasks for parallel data fetching
    tasks = []
    for symbol in symbols_to_use:
        for timeframe in config.TIMEFRAMES:
            # Calculate date range
            end_time = datetime.now()
            start_time = end_time - timedelta(days=config.DAYS_TO_FETCH)
            
            # Use the correct method name
            task = asyncio.create_task(
                fetcher.fetch_and_save_simple(symbol, timeframe, 
                                           start_time, end_time)
            )
            tasks.append(task)
    
    # Wait for all historical data fetching to complete
    if tasks:
        print(f"Fetching data for {len(tasks)} symbol/timeframe combinations...")
        await asyncio.gather(*tasks)
    print("Historical data fetching completed.")
    
    # Merge historical and real-time data if WebSocket is enabled
    if config.ENABLE_WEBSOCKET and ws_handler:
        print("Merging historical and real-time data...")
        for symbol in symbols_to_use:
            for timeframe in config.TIMEFRAMES:
                # Get historical data
                filename = os.path.join(config.DATA_DIR, f"{symbol}_{timeframe}.csv")
                historical_data = []
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        reader = csv.DictReader(f)
                        historical_data = list(reader)
                
                # Get real-time data
                realtime_data = ws_handler.get_real_time_data(symbol, timeframe)
                
                # Merge data
                merged_data = merge_historical_realtime(historical_data, realtime_data)
                
                # Save merged data
                with open(filename, 'w', newline='') as f:
                    fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(merged_data)
                
                print(f"Merged data for {symbol} {timeframe}: {len(historical_data)} historical + {len(realtime_data)} real-time")
        
        print("Data merging completed.")
    
    # Run integrity check if enabled
    if config.RUN_INTEGRITY_CHECK:
        print("Running integrity check...")
        integrity_checker = DataIntegrityChecker(config)
        results = integrity_checker.check_all_files()
        
        print("\n"+"="*60)
        print("INTEGRITY CHECK RESULTS")
        print("="*60)
        print(f"Files checked: {results['files_checked']}")
        print(f"Files with issues: {results['files_with_issues']}")
        print(f"Total gaps: {results['total_gaps']}")
        print(f"Total duplicates: {results['total_duplicates']}")
        print(f"Total invalid candles: {results['total_invalid_candles']}")
        print("="*60)
    
    # Fill gaps if enabled
    if config.RUN_GAP_FILLING:
        print("Filling gaps in data...")
        integrity_checker = DataIntegrityChecker(config)
        integrity_checker.fill_all_gaps()
        print("Gap filling completed.")
    
    # Continue with live updates if WebSocket is enabled
    if config.ENABLE_WEBSOCKET and ws_handler:
        print("\n" + "="*60)
        print("LIVE DATA COLLECTION MODE")
        print("="*60)
        print(f"WebSocket is running and collecting live data for {len(symbols_to_use)} symbols...")
        print("Watch for '🔥 Processing confirmed candle' and '✓ LIVE UPDATE' messages as new candles arrive.")
        print("Press Ctrl+C to stop...")
        
        try:
            while ws_handler.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping WebSocket...")
            ws_handler.stop()
            await asyncio.sleep(1)  # Give time for cleanup
            try:
                await ws_task
            except:
                pass  # Ignore errors when stopping
    else:
        print("\nHistorical data collection completed. Exiting...")
    
    # Run integrity check if enabled
    if config.RUN_INTEGRITY_CHECK:
        print("Running integrity check...")
        integrity_checker = DataIntegrityChecker(config)
        results = integrity_checker.check_all_files()
        
        print("\n"+"="*60)
        print("INTEGRITY CHECK RESULTS")
        print("="*60)
        print(f"Files checked: {results['files_checked']}")
        print(f"Files with issues: {results['files_with_issues']}")
        print(f"Total gaps: {results['total_gaps']}")
        print(f"Total duplicates: {results['total_duplicates']}")
        print(f"Total invalid candles: {results['total_invalid_candles']}")
        print("="*60)
    
    # Fill gaps if enabled
    if config.RUN_GAP_FILLING:
        print("Filling gaps in data...")
        integrity_checker = DataIntegrityChecker(config)
        integrity_checker.fill_all_gaps()
        print("Gap filling completed.")
    
    # Continue with live updates if WebSocket is enabled
    if config.ENABLE_WEBSOCKET and ws_handler:
        print("\n" + "="*60)
        print("LIVE DATA COLLECTION MODE")
        print("="*60)
        print(f"WebSocket is running and collecting live data for {len(symbols_to_use)} symbols...")
        print("Watch for '🔥 Processing confirmed candle' and '✓ LIVE UPDATE' messages as new candles arrive.")
        print("Press Ctrl+C to stop...")
        
        try:
            while ws_handler.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping WebSocket...")
            ws_handler.stop()
            await asyncio.sleep(1)  # Give time for cleanup
            try:
                await ws_task
            except:
                pass  # Ignore errors when stopping
    else:
        print("\nHistorical data collection completed. Exiting...")

def main():
    """Main entry point for the data collection application"""
    global config
    
    config = DataCollectionConfig()
    
    # Print configuration
    print(f"Configuration:")
    print(f" Days: {config.DAYS_TO_FETCH}")
    print(f" Data mode: {'Limited to 50 entries' if config.LIMIT_TO_50_ENTRIES else 'Full historical data'}")
    print(f" Symbols: {'All from Bybit' if config.FETCH_ALL_SYMBOLS else f'{len(config.SYMBOLS)} configured'}")
    print(f" Timeframes: {config.TIMEFRAMES}")
    print(f" WebSocket: {'Enabled' if config.ENABLE_WEBSOCKET else 'Disabled'}")
    print(f" Integrity Check: {'Enabled' if config.RUN_INTEGRITY_CHECK else 'Disabled'}")
    print(f" Gap Filling: {'Enabled' if config.RUN_GAP_FILLING else 'Disabled'}")
    print(f" Test Mode: {'Enabled' if config.TEST_WEBSOCKET else 'Disabled'}")
    print("="*60)
    
    # Run the async data collection
    try:
        asyncio.run(run_data_collection())
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()'''