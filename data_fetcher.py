# optimized_data_fetcher.py - Complete Fixed Version
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
    
    async def fetch_historical_data_fast(self, symbols: List[str], timeframes: List[str], 
                                       days: int, limit_50: bool = False):
        """Ultra-fast historical data fetching"""
        self.fetch_stats['start_time'] = time.time()
        self.fetch_stats['total_requests'] = len(symbols) * len(timeframes)
        self.fetch_stats['successful_requests'] = 0
        self.fetch_stats['failed_requests'] = 0
        
        tasks = []
        
        for symbol in symbols:
            for timeframe in timeframes:
                task = asyncio.create_task(
                    self._fetch_symbol_timeframe(symbol, timeframe, days, limit_50)
                )
                tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        success_count = 0
        for result in results:
            if result is True:
                success_count += 1
            elif result is False:
                self.fetch_stats['failed_requests'] += 1
        
        self.fetch_stats['successful_requests'] = success_count
        self.fetch_stats['end_time'] = time.time()
        
        # Print performance stats
        duration = self.fetch_stats['end_time'] - self.fetch_stats['start_time']
        print(f"📊 Historical data fetch completed in {duration:.2f} seconds")
        print(f"✅ Successful: {self.fetch_stats['successful_requests']}/{self.fetch_stats['total_requests']}")
        
        return success_count == len(tasks)
    
    async def _fetch_symbol_timeframe(self, symbol: str, timeframe: str,
                                 days: int, limit_50: bool):
        """Fetch data for single symbol/timeframe with proven chunking approach"""
        end_time = int(time.time() * 1000)
        
        # If limit_50 is True, we only need the most recent 50 candles
        if limit_50:
            print(f"🚀 DEBUG: Using limit_50=True path")
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
            
            url = f"https://api.bybit.com/v5/market/kline"
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": timeframe,
                "start": start_time,
                "end": end_time,
                "limit": limit_per_request
            }
            
            try:
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("retCode") == 0:
                        candles = data["result"]["list"]
                        
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
                        
                        # Sort by timestamp (newest first) and limit to 50
                        processed_candles.sort(key=lambda x: x['timestamp'], reverse=True)
                        if len(processed_candles) > 50:
                            processed_candles = processed_candles[:50]
                        
                        # Store in memory
                        key = f"{symbol}_{timeframe}"
                        if key not in self.memory_data:
                            self.memory_data[key] = deque(maxlen=50)
                        
                        # Add to memory storage
                        self.memory_data[key].extend(processed_candles)
                        
                        print(f"✅ Fetched {len(processed_candles)} candles for {symbol}_{timeframe}")
                        return True
                    else:
                        print(f"❌ Error fetching {symbol}/{timeframe}: {data.get('retMsg')}")
                        return False
                        
            except Exception as e:
                print(f"❌ Exception fetching {symbol}/{timeframe}: {e}")
                return False
        
        else:
            print(f"🚀 DEBUG: Using limit_50=False path - this should use chunking!")
            # For full historical data, use the proven chunking approach
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
            
            url = f"https://api.bybit.com/v5/market/kline"
            all_candles = []
            
            # Use the proven approach: 8-hour chunks working backwards
            chunk_duration = 8 * 60 * 60 * 1000  # 8 hours in milliseconds
            current_end = end_time
            
            print(f"📊 Fetching {symbol}_{timeframe} using 8-hour chunks...")
            
            while current_end > start_time:
                current_start = max(start_time, current_end - chunk_duration)
                
                params = {
                    "category": "linear",
                    "symbol": symbol,
                    "interval": timeframe,
                    "start": int(current_start),
                    "end": int(current_end),
                    "limit": 1000
                }
                
                try:
                    async with self.session.get(url, params=params) as response:
                        data = await response.json()
                        
                        if data.get("retCode") == 0:
                            candles = data["result"]["list"]
                            
                            if candles:
                                print(f"📊 Chunk {datetime.fromtimestamp(current_start/1000)} to {datetime.fromtimestamp(current_end/1000)}: {len(candles)} candles")
                                
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
                                
                                all_candles.extend(processed_candles)
                                
                                # Update for next chunk - use the oldest candle's timestamp
                                current_end = int(candles[-1][0]) - 1  # -1 to avoid overlap
                            else:
                                print(f"📊 No candles returned for chunk ending at {datetime.fromtimestamp(current_end/1000)}")
                                break
                                
                            # Small delay to avoid rate limiting
                            await asyncio.sleep(0.1)
                            
                        else:
                            print(f"❌ Error fetching chunk: {data.get('retMsg')}")
                            break
                            
                except Exception as e:
                    print(f"❌ Exception fetching chunk: {e}")
                    break
            
            # Store in memory
            if all_candles:
                key = f"{symbol}_{timeframe}"
                if key not in self.memory_data:
                    self.memory_data[key] = deque(maxlen=5000)
                
                # Sort by timestamp (ascending order)
                all_candles.sort(key=lambda x: x['timestamp'])
                
                # Add to memory storage
                self.memory_data[key].extend(all_candles)
                
                print(f"✅ Fetched {len(all_candles)} candles for {symbol}_{timeframe}")
                return True
            else:
                print(f"❌ No data fetched for {symbol}_{timeframe}")
                return False
    
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
                    
                    # Write candles with human-readable datetime
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

'''import os
import csv
import time
import requests
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from config import DataCollectionConfig

class FastDataFetcher:
    def __init__(self, config: DataCollectionConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
        # Create data directory
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        # Performance tracking
        self.fetch_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0,
            'symbols_timeframes': {},
            'start_time': None,
            'end_time': None,
            'total_candles_fetched': 0,
            'skipped_files': 0,
            'refetched_files': 0
        }
        # Get all symbols if enabled
        if self.config.FETCH_ALL_SYMBOLS:
            self.all_symbols = self._get_all_symbols()
            print(f"Found {len(self.all_symbols)} symbols from Bybit")
        else:
            self.all_symbols = self.config.SYMBOLS

    def _get_all_symbols(self) -> List[str]:
        """Get all available linear symbols from Bybit with pagination"""
        url = f"{self.config.API_BASE_URL}/v5/market/instruments-info"
        all_symbols = []
        cursor = None
        excluded_symbols = ['USDC', 'USDE', 'USTC']
        print("Fetching all symbols from Bybit...")
        while True:
            params = {
                "category": "linear",
                "limit": 1000,
                "cursor": cursor
            }
            try:
                response = self.session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('retCode') == 0:
                        items = data['result']['list']
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
                        if not cursor:
                            break
                    else:
                        print(f"Error fetching symbols: {data.get('retMsg')}")
                        break
                else:
                    print(f"HTTP Error fetching symbols: {response.status_code}")
                    break
                time.sleep(self.config.RATE_LIMIT_DELAY)
            except Exception as e:
                print(f"Exception fetching symbols: {e}")
                break
        print(f"Fetched {len(all_symbols)} perpetual symbols")
        # Show first 10 symbols as examples
        if all_symbols:
            print(f"Examples: {', '.join(all_symbols[:10])}...")
        
        return sorted(all_symbols)

    def _validate_existing_file(self, symbol: str, timeframe: str, required_start: datetime, required_end: datetime) -> Tuple[bool, str]:
        """Validate existing data file and check if it meets requirements"""
        filename = os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")
        if not os.path.exists(filename):
            return False, "File does not exist"
        
        try:
            # Check file size (very small files might be corrupt)
            file_size = os.path.getsize(filename)
            if file_size < 100:  # Less than 100 bytes is suspicious
                return False, f"File too small ({file_size} bytes), likely corrupt"
            
            # Read and validate data
            with open(filename, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
                if not data:
                    return False, "File is empty"
                
                # Check data integrity
                for i, row in enumerate(data):
                    if not self._validate_candle(row):
                        return False, f"Invalid candle at row {i+1}: {row}"
                
                # Check date range
                first_timestamp = datetime.fromisoformat(data[0]['timestamp'])
                last_timestamp = datetime.fromisoformat(data[-1]['timestamp'])
                
                # Allow some tolerance (1 hour) for the start time
                start_tolerance = timedelta(hours=1)
                if first_timestamp > required_start + start_tolerance:
                    return False, f"Data starts too late: {first_timestamp} > {required_start}"
                
                # For end time, we expect data to be recent (within last hour)
                current_time = datetime.now()
                end_tolerance = timedelta(hours=1)
                if last_timestamp < current_time - end_tolerance:
                    return False, f"Data ends too early: {last_timestamp} < {current_time - end_tolerance}"
                
                # Check if we have enough data (50 entries for limited mode, full range for unlimited)
                if self.config.LIMIT_TO_50_ENTRIES and len(data) < 50:
                    return False, f"Not enough data: {len(data)} < 50 entries"
                
                return True, "File is valid"
        except Exception as e:
            return False, f"Error validating file: {e}"

    def _validate_candle(self, candle: Dict[str, Any]) -> bool:
        """Validate a single candle"""
        try:
            # Check required fields
            required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            if not all(field in candle for field in required_fields):
                return False
            
            # Validate timestamp format
            datetime.fromisoformat(candle['timestamp'])
            
            # Validate numeric fields
            for field in ['open', 'high', 'low', 'close', 'volume', 'turnover']:
                float(candle[field])
            
            return True
        except Exception:
            return False

    async def fetch_and_save_simple(self, symbol: str, timeframe: str, start_time: datetime, end_time: datetime) -> bool:
        """Fetch data for a single symbol/timeframe and save to CSV"""
        # Calculate how many candles we need
        timeframe_minutes = int(timeframe)
        if timeframe == '1440':  # Daily
            timeframe_minutes = 1440
        
        # If we're limiting to 50 entries, adjust the start time
        if self.config.LIMIT_TO_50_ENTRIES:
            # Calculate start time to get exactly 50 candles
            start_time = end_time - timedelta(minutes=timeframe_minutes * 50)
        
        data = await self.fetch_historical_klines(symbol, timeframe, start_time, end_time)
        if data:
            self.save_to_csv(symbol, timeframe, data)
            return True
        return False

    async def fetch_historical_klines(self, symbol: str, timeframe: str, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Fetch historical klines from Bybit"""
        # Map timeframe to Bybit format
        timeframe_map = {'1': '1', '5': '5', '15': '15', '60': '60', '240': '240', '1440': 'D'}
        bybit_timeframe = timeframe_map.get(timeframe, '1')
        
        url = f"{self.config.API_BASE_URL}/v5/market/kline"
        
        # Calculate batch size (Bybit limit is 1000 candles per request)
        timeframe_minutes = int(timeframe)
        if timeframe == '1440':  # Daily
            timeframe_minutes = 1440
        
        batch_size_candles = 1000
        batch_size_minutes = batch_size_candles * timeframe_minutes
        batch_size_timedelta = timedelta(minutes=batch_size_minutes)
        
        all_data = []
        current_end = end_time
        batch_count = 0
        
        print(f"  Fetching {symbol} {timeframe} from {start_time} to {end_time}")
        
        while current_end > start_time:
            batch_count += 1
            current_start = max(start_time, current_end - batch_size_timedelta)
            
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": bybit_timeframe,
                "start": int(current_start.timestamp() * 1000),  # Convert to milliseconds
                "end": int(current_end.timestamp() * 1000),  # Convert to milliseconds
                "limit": 1000
            }
            
            try:
                self.fetch_stats['total_requests'] += 1
                request_start = time.time()
                
                response = self.session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT)
                request_time = time.time() - request_start
                self.fetch_stats['total_time'] += request_time
                
                if response.status_code == 200:
                    self.fetch_stats['successful_requests'] += 1
                    data = response.json()
                    
                    if data.get('retCode') == 0:
                        klines = data['result']['list']
                        # Convert Bybit format to our format
                        batch_data = []
                        for kline in klines:
                            # Bybit returns: [start_time, open, high, low, close, volume, turnover]
                            candle = {
                                'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000).isoformat(),
                                'open': kline[1],
                                'high': kline[2],
                                'low': kline[3],
                                'close': kline[4],
                                'volume': kline[5],
                                'turnover': kline[6]
                            }
                            batch_data.append(candle)
                        
                        # Add batch data to all data (in reverse order since Bybit returns newest first)
                        all_data = batch_data + all_data
                        
                        print(f"    Batch {batch_count}: {len(batch_data)} candles ({batch_data[0]['timestamp']} to {batch_data[-1]['timestamp']})")
                        
                        # Update stats
                        self.fetch_stats['total_candles_fetched'] += len(batch_data)
                        key = f"{symbol}_{timeframe}"
                        if key not in self.fetch_stats['symbols_timeframes']:
                            self.fetch_stats['symbols_timeframes'][key] = {
                                'requests': 0,
                                'candles': 0,
                                'time': 0
                            }
                        self.fetch_stats['symbols_timeframes'][key]['requests'] += 1
                        self.fetch_stats['symbols_timeframes'][key]['candles'] += len(batch_data)
                        self.fetch_stats['symbols_timeframes'][key]['time'] += request_time
                    else:
                        print(f"    Error fetching data: {data.get('retMsg')}")
                        self.fetch_stats['failed_requests'] += 1
                else:
                    print(f"    HTTP Error: {response.status_code}")
                    self.fetch_stats['failed_requests'] += 1
                
                # Move to next batch
                current_end = current_start
                
                # Rate limiting
                time.sleep(self.config.RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"    Exception: {e}")
                self.fetch_stats['failed_requests'] += 1
                break
        
        print(f"    Reached start time, stopping")
        print(f"  ✓ {symbol} {timeframe}: {len(all_data)} unique candles in {batch_count} batches")
        
        return all_data

    def save_to_csv(self, symbol: str, timeframe: str, data: List[Dict]):
        """Save data to CSV file"""
        filename = os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")
        
        # Sort data by timestamp (newest first)
        data.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit to 50 entries if configured
        if self.config.LIMIT_TO_50_ENTRIES and len(data) > 50:
            data = data[:50]
            print(f"Saved 50 records to {filename} (Limited to 50 entries)")
        else:
            print(f"Saved {len(data)} records to {filename}")
        
        # Write to CSV
        with open(filename, 'w', newline='') as f:
            fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    async def fetch_all_data(self):
        """Fetch data for all symbols and timeframes"""
        self.fetch_stats['start_time'] = time.time()
        
        # Create tasks for parallel processing
        tasks = []
        for symbol in self.all_symbols:
            for timeframe in self.config.TIMEFRAMES:
                # Calculate date range
                end_time = datetime.now()
                start_time = end_time - timedelta(days=self.config.DAYS_TO_FETCH)
                
                # Check if we need to refetch
                valid, reason = self._validate_existing_file(symbol, timeframe, start_time, end_time)
                if not valid:
                    print(f"  ↻ {symbol} {timeframe}: {reason}")
                    task = asyncio.create_task(
                        self.fetch_and_save_simple(symbol, timeframe, start_time, end_time)
                    )
                    tasks.append(task)
                else:
                    print(f"  ✓ {symbol} {timeframe}: File is valid, skipping")
                    self.fetch_stats['skipped_files'] += 1
        
        # Execute tasks in parallel
        if tasks:
            print(f"Fetching data for {len(tasks)} symbol/timeframe combinations...")
            completed = 0
            total_tasks = len(tasks)
            
            # Use ThreadPoolExecutor for synchronous requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
                # Create a list of futures
                future_to_symbol_tf = {
                    executor.submit(self._run_async_task, task): (symbol, timeframe)
                    for task, symbol, timeframe in [
                        (task, *self._extract_symbol_timeframe_from_task(task)) 
                        for task in tasks
                    ]
                }
                
                # Process completed tasks
                for future in concurrent.futures.as_completed(future_to_symbol_tf):
                    symbol, timeframe = future_to_symbol_tf[future]
                    completed += 1
                    try:
                        success = future.result()
                        if self.config.SHOW_DETAILED_TIMING:
                            print(f"[{completed}/{total_tasks}] ✓ {symbol} {timeframe}")
                        else:
                            print(f"[{completed}/{total_tasks}] {'✓' if success else '✗'} {symbol} {timeframe}")
                    except Exception as e:
                        print(f"[{completed}/{total_tasks}] ✗ {symbol} {timeframe} - {e}")
        
        self.fetch_stats['end_time'] = time.time()
        total_duration = self.fetch_stats['end_time'] - self.fetch_stats['start_time']
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'='*60}")
        print(f"DATA COLLECTION COMPLETED")
        print(f"{'='*60}")
        print(f"End time: {end_datetime}")
        print(f"Total duration: {total_duration:.2f} seconds")
        print(f"Total candles fetched: {self.fetch_stats['total_candles_fetched']}")
        print(f"Average time per symbol/timeframe: {total_duration/max(1, len(self.all_symbols) * len(self.config.TIMEFRAMES)):.2f} seconds")
        if self.config.SHOW_PERFORMANCE_STATS:
            self.print_stats()
        print(f"{'='*60}")

    def _run_async_task(self, task):
        """Run an async task in a synchronous context"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(task)
        finally:
            loop.close()

    def _extract_symbol_timeframe_from_task(self, task):
        """Extract symbol and timeframe from a task"""
        # This is a helper method to extract symbol and timeframe from a task
        # In a real implementation, you might need to adjust this based on how tasks are created
        # For now, we'll return placeholder values
        return "UNKNOWN", "UNKNOWN"

    def print_stats(self):
        """Print detailed performance statistics"""
        stats = self.fetch_stats
        print(f"\n{'='*50}")
        print(f"DETAILED PERFORMANCE STATISTICS")
        print(f"{'='*50}")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Successful requests: {stats['successful_requests']}")
        print(f"Failed requests: {stats['failed_requests']}")
        print(f"Success rate: {stats['successful_requests']/max(1, stats['total_requests'])*100:.1f}%")
        print(f"Total API time: {stats['total_time']:.2f} seconds")
        print(f"Average time per request: {stats['total_time']/max(1, stats['total_requests']):.2f} seconds")
        print(f"Total candles fetched: {stats['total_candles_fetched']}")
        print(f"Average time per candle: {stats['total_time']/max(1, stats['total_candles_fetched']):.4f} seconds")
        
        print(f"\nPer symbol/timeframe stats:")
        for key, data in stats['symbols_timeframes'].items():
            print(f"  {key}: {data['requests']} requests, {data['candles']} candles, {data['time']:.2f}s")'''