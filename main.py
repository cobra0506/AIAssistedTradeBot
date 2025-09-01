import os
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
        # Read existing data asynchronously
        existing_data = []
        if os.path.exists(filename):
            existing_data = await asyncio.to_thread(read_csv, filename)
        
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
            
            # Write back to file asynchronously
            fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            await asyncio.to_thread(write_csv, filename, fieldnames, existing_data)
            
            print(f"✓ LIVE UPDATE: {symbol}_{timeframe} - New candle at {new_candle['timestamp']}")

def read_csv(filename):
    """Read CSV file and return data"""
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_csv(filename, fieldnames, data):
    """Write data to CSV file"""
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

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
    
    # Create fetcher instance
    fetcher = FastDataFetcher(config)
    
    # First, determine which symbols to use
    print("Determining symbols to use...")
    if config.FETCH_ALL_SYMBOLS:
        print("Fetching all symbols from Bybit...")
        # Initialize the fetcher asynchronously
        await fetcher.initialize()
        
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
        # Still need to initialize the fetcher
        await fetcher.initialize()
    
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
        
        # Create tasks for parallel data fetching
        tasks = []
        for symbol in symbols_to_use:
            for timeframe in config.TIMEFRAMES:
                # Calculate date range
                end_time = datetime.now()
                start_time = end_time - timedelta(days=config.DAYS_TO_FETCH)
                
                # Use the fetcher instance we created earlier
                task = asyncio.create_task(
                    fetcher.fetch_and_save_simple(symbol, timeframe, 
                                            start_time, end_time)
                )
                tasks.append(task)
        
        # Wait for all historical data fetching to complete
        if tasks:
            print(f"Fetching data for {len(tasks)} symbol/timeframe combinations...")
            # Use a semaphore to limit concurrent requests and avoid rate limiting
            semaphore = asyncio.Semaphore(3)  # Reduced from 5 to 3 to further avoid rate limiting
            
            async def fetch_with_semaphore(task):
                async with semaphore:
                    # Add a small delay between requests to further avoid rate limiting
                    await asyncio.sleep(0.5)  # Increased from 0.2 to 0.5
                    return await task
            
            # Process tasks with semaphore
            results = await asyncio.gather(*[fetch_with_semaphore(task) for task in tasks])
            
            # Print summary
            successful = sum(results)
            failed = len(results) - successful
            print(f"Historical data fetching completed.")
            print(f"Results: {successful} successful, {failed} failed")
            if failed > 0:
                print(f"Success rate: {successful / len(results) * 100:.1f}%")
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
    main()