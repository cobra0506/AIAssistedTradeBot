# optimized_data_fetcher.py - Fixed to save data in correct chronological order
import asyncio
import aiohttp
import csv
import os
import time
from collections import deque
from typing import Dict, List, Any
from datetime import datetime
from config import DataCollectionConfig

class OptimizedDataFetcher:
    def __init__(self, config):
        self.config = config
        self.memory_data = {}  # symbol -> timeframe -> deque
        self.session = None
        self.fetch_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'start_time': None,
            'end_time': None
        }
        
    async def initialize(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)  # High connection limit
        )
    
    async def _get_all_symbols(self) -> List[str]:
        """Get all available linear symbols from Bybit with pagination"""
        url = f"{self.config.API_BASE_URL}/v5/market/instruments-info"
        all_symbols = []
        cursor = None
        excluded_symbols = ['USDC', 'USDE', 'USTC']
        
        print("Fetching all symbols from Bybit...")
        
        while True:
            # Build params dict, ensuring None values are filtered out
            params = {
                "category": "linear",
                "limit": 1000
            }
            # Only add cursor if it's not None
            if cursor is not None:
                params["cursor"] = cursor
                
            try:
                print(f"Making request with params: {params}")
                async with self.session.get(url, params=params, timeout=30) as response:
                    print(f"Response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        print(f"Response retCode: {data.get('retCode')}")
                        if data.get('retCode') == 0:
                            items = data['result']['list']
                            print(f"Received {len(items)} items")
                            
                            # Filter symbols with correct field values
                            symbols = [
                                item['symbol'] for item in items
                                if not any(excl in item['symbol'] for excl in excluded_symbols)
                                and "-" not in item['symbol']
                                and item['symbol'].endswith('USDT')
                                and item.get('contractType') == 'LinearPerpetual'
                                and item.get('status') == 'Trading'
                            ]
                            all_symbols.extend(symbols)
                            
                            cursor = data['result'].get('nextPageCursor')
                            print(f"Next cursor: {cursor}")
                            
                            if not cursor:
                                break
                        else:
                            print(f"Error fetching symbols: {data.get('retMsg')}")
                            break
                    else:
                        print(f"HTTP Error fetching symbols: {response.status}")
                        break
                        
            except Exception as e:
                print(f"Exception fetching symbols: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"Fetched {len(all_symbols)} perpetual symbols")
        
        # Show first 10 symbols as examples
        if all_symbols:
            print(f"Examples: {', '.join(all_symbols[:10])}...")
        
        return sorted(all_symbols)

    async def fetch_historical_data_fast(self, symbols: List[str], timeframes: List[str], 
                                   days: int, limit_50: bool = False):
        """Ultra-fast historical data fetching with batching and rate limiting"""
        self.fetch_stats['start_time'] = time.time()
        self.fetch_stats['total_requests'] = len(symbols) * len(timeframes)
        self.fetch_stats['successful_requests'] = 0
        self.fetch_stats['failed_requests'] = 0
        
        tasks = []
        
        # Process in batches to avoid overwhelming the API
        batch_size = self.config.BULK_BATCH_SIZE
        
        print(f"🔄 Processing {len(symbols)} symbols in batches of {batch_size}")
        
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            
            print(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch_symbols)} symbols)")
            
            batch_tasks = []
            for symbol in batch_symbols:
                for timeframe in timeframes:
                    task = asyncio.create_task(
                        self._fetch_symbol_timeframe(symbol, timeframe, days, limit_50)
                    )
                    batch_tasks.append(task)
            
            # Execute batch tasks concurrently
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if result is True:
                    self.fetch_stats['successful_requests'] += 1
                elif result is False:
                    self.fetch_stats['failed_requests'] += 1
                elif isinstance(result, Exception):
                    print(f"❌ Exception in batch: {result}")
                    self.fetch_stats['failed_requests'] += 1
            
            # Add delay between batches
            if i + batch_size < len(symbols):  # If there are more batches
                delay_seconds = self.config.BULK_REQUEST_DELAY_MS / 1000 * 2  # Longer delay between batches
                print(f"⏳ Waiting {delay_seconds} seconds before next batch...")
                await asyncio.sleep(delay_seconds)
        
        self.fetch_stats['end_time'] = time.time()
        
        # Print performance stats
        duration = self.fetch_stats['end_time'] - self.fetch_stats['start_time']
        success_rate = (self.fetch_stats['successful_requests'] / self.fetch_stats['total_requests']) * 100
        
        print(f"📊 Historical data fetch completed in {duration:.2f} seconds")
        print(f"✅ Successful: {self.fetch_stats['successful_requests']}/{self.fetch_stats['total_requests']} ({success_rate:.1f}%)")
        
        return self.fetch_stats['failed_requests'] == 0
    
    async def _fetch_symbol_timeframe(self, symbol: str, timeframe: str,
                                 days: int, limit_50: bool):
        """Fetch data for single symbol/timeframe with rate limiting and retry logic"""
        print(f"🔄 Fetching {symbol}_{timeframe}...")
        
        end_time = int(time.time() * 1000)
        
        # If limit_50 is True, we only need the most recent 50 candles
        if limit_50:
            # For limited mode, just fetch the most recent 50 candles
            limit_per_request = 50
            
            # Estimate how much time we need to go back to get at least 50 candles
            timeframe_minutes = int(timeframe)
            if timeframe_minutes <= 1:  # 1m or similar
                start_time = end_time - (60 * 60 * 1000)  # Go back 1 hour
            elif timeframe_minutes <= 5:  # 5m or similar
                start_time = end_time - (5 * 60 * 60 * 1000)  # Go back 5 hours
            elif timeframe_minutes <= 15:  # 15m or similar
                start_time = end_time - (15 * 60 * 60 * 1000)  # Go back 15 hours
            else:
                start_time = end_time - (24 * 60 * 60 * 1000)  # Go back 1 day
            
            # Use the rate-limited request method
            result = await self._make_rate_limited_request(symbol, timeframe, start_time, end_time, limit_per_request)
            
            if result:
                # Store in memory
                key = f"{symbol}_{timeframe}"
                if key not in self.memory_data:
                    self.memory_data[key] = deque(maxlen=50)
                
                # Sort by timestamp (newest first) and limit to 50
                result.sort(key=lambda x: x['timestamp'], reverse=True)
                if len(result) > 50:
                    result = result[:50]
                
                # Add to memory storage
                self.memory_data[key].extend(result)
                
                print(f"✅ Fetched {len(result)} candles for {symbol}_{timeframe}")
                return True
            else:
                print(f"❌ Failed to fetch {symbol}_{timeframe}")
                return False
        
        else:
            # For full historical data, use chunking with rate limiting
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            all_candles = []
            
            # Use the proven approach: 8-hour chunks working backwards
            chunk_duration = 8 * 60 * 60 * 1000  # 8 hours in milliseconds
            current_end = end_time
            
            print(f"📊 Fetching {symbol}_{timeframe} using 8-hour chunks...")
            
            successful_chunks = 0
            failed_chunks = 0
            
            while current_end > start_time:
                current_start = max(start_time, current_end - chunk_duration)
                
                # Make rate-limited request for this chunk
                chunk_candles = await self._make_rate_limited_request(
                    symbol, timeframe, int(current_start), int(current_end), 1000
                )
                
                if chunk_candles:
                    all_candles.extend(chunk_candles)
                    successful_chunks += 1
                    
                    # Update for next chunk - use the oldest candle's timestamp
                    current_end = int(chunk_candles[-1]['timestamp']) - 1  # -1 to avoid overlap
                    
                    print(f"📊 Chunk {successful_chunks + failed_chunks + 1}: Got {len(chunk_candles)} candles")
                else:
                    failed_chunks += 1
                    print(f"❌ Failed to fetch chunk {successful_chunks + failed_chunks + 1}")
                    
                    # If we fail too many chunks, break early
                    if failed_chunks >= 3:
                        print(f"❌ Too many failed chunks ({failed_chunks}), stopping early")
                        break
                    
                    # Try to continue with the next chunk
                    current_end = current_start - 1
                    
                # Add delay between chunks
                await asyncio.sleep(self.config.BULK_REQUEST_DELAY_MS / 1000)
            
            # Store in memory
            if all_candles:
                key = f"{symbol}_{timeframe}"
                if key not in self.memory_data:
                    self.memory_data[key] = deque(maxlen=5000)
                
                # Sort by timestamp (ascending order)
                all_candles.sort(key=lambda x: x['timestamp'])
                
                # Add to memory storage
                self.memory_data[key].extend(all_candles)
                
                print(f"✅ Fetched {len(all_candles)} candles for {symbol}_{timeframe} ({successful_chunks} successful, {failed_chunks} failed)")
                return True
            else:
                print(f"❌ No data fetched for {symbol}_{timeframe}")
                return False

    async def _make_rate_limited_request(self, symbol: str, timeframe: str, 
                                    start_time: int, end_time: int, limit: int):
        """Make a rate-limited request to Bybit API with retry logic"""
        url = f"https://api.bybit.com/v5/market/kline"
        
        max_retries = self.config.BULK_MAX_RETRIES
        retry_delay = self.config.BULK_RETRY_DELAY_MS / 1000  # Convert to seconds
        
        for attempt in range(max_retries):
            try:
                # Add delay before each request (except the first one)
                if attempt > 0:
                    await asyncio.sleep(retry_delay)
                    # Exponential backoff
                    retry_delay *= 2
                
                params = {
                    "category": "linear",
                    "symbol": symbol,
                    "interval": timeframe,
                    "start": start_time,
                    "end": end_time,
                    "limit": limit
                }
                
                async with self.session.get(url, params=params) as response:
                    # Check if we got a rate limiting response (HTML instead of JSON)
                    content_type = response.headers.get('Content-Type', '')
                    
                    if 'text/html' in content_type or 'text/plain' in content_type:
                        # This is likely a rate limiting error
                        print(f"❌ Rate limited for {symbol}_{timeframe} (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            print(f"⏳ Retrying in {retry_delay} seconds...")
                            continue  # Retry
                        else:
                            print(f"❌ Max retries reached for {symbol}_{timeframe}")
                            return None
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("retCode") == 0:
                            candles = data["result"]["list"]
                            
                            if candles:
                                # Process candles
                                processed_candles = []
                                for candle in candles:
                                    processed = {
                                        'timestamp': int(candle[0]),
                                        'open': float(candle[1]),
                                        'high': float(candle[2]),
                                        'low': float(candle[3]),
                                        'close': float(candle[4]),
                                        'volume': float(candle[5])
                                    }
                                    processed_candles.append(processed)
                                
                                return processed_candles
                            else:
                                return []
                        else:
                            print(f"❌ API error for {symbol}_{timeframe}: {data.get('retMsg')}")
                            return None
                    elif response.status == 403:
                        print(f"❌ 403 Forbidden for {symbol}_{timeframe} (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            print(f"⏳ Retrying in {retry_delay} seconds...")
                            continue  # Retry
                        else:
                            print(f"❌ Max retries reached for {symbol}_{timeframe}")
                            return None
                    else:
                        print(f"❌ HTTP {response.status} for {symbol}_{timeframe}")
                        return None
                        
            except Exception as e:
                print(f"❌ Exception for {symbol}_{timeframe}: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    continue  # Retry
                else:
                    print(f"❌ Max retries reached for {symbol}_{timeframe}")
                    return None
        
        return None
   
    def get_memory_data(self):
        """Access to in-memory data (like RedoneTradeBot)"""
        return self.memory_data
    
    async def save_to_csv(self, directory: str = "data"):
        """Save all data to CSV at once (reduces I/O overhead)"""
        os.makedirs(directory, exist_ok=True)
        
        for key, candles in self.memory_data.items():
            if candles:
                symbol, timeframe = key.split('_')
                filename = os.path.join(directory, f"{symbol}_{timeframe}.csv")
                
                with open(filename, 'w', newline='') as f:
                    # Create fieldnames with both timestamp and datetime
                    fieldnames = ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    # Write candles with human-readable datetime in chronological order
                    for candle in candles:
                        # Convert timestamp to datetime
                        dt = datetime.fromtimestamp(candle['timestamp'] / 1000)
                        datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Create a new row with both timestamp and datetime
                        row = candle.copy()
                        row['datetime'] = datetime_str
                        writer.writerow(row)
                
                print(f"💾 Saved {len(candles)} candles to {filename}")
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()