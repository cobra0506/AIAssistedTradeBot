import os
import csv
import time
import requests
import concurrent.futures
import random
import asyncio
import aiohttp
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
        
        # Initialize all_symbols as empty list
        self.all_symbols = []

    async def initialize(self):
        """Initialize the fetcher asynchronously"""
        # Get all symbols if enabled
        if self.config.FETCH_ALL_SYMBOLS:
            self.all_symbols = await self._get_all_symbols_async()
            print(f"Found {len(self.all_symbols)} symbols from Bybit")
        else:
            self.all_symbols = self.config.SYMBOLS

    async def _get_all_symbols_async(self) -> List[str]:
        """Get all available linear symbols from Bybit with pagination (async version)"""
        url = f"{self.config.API_BASE_URL}/v5/market/instruments-info"
        all_symbols = []
        cursor = None
        excluded_symbols = ['USDC', 'USDE', 'USTC']
        print("Fetching all symbols from Bybit...")
        
        async with aiohttp.ClientSession() as session:
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
                    async with session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT) as response:
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

    def _validate_candle(self, candle: Dict) -> bool:
        """Validate a single candle record"""
        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        
        # Check all required fields are present
        for field in required_fields:
            if field not in candle:
                return False
        
        # Check timestamp format
        try:
            datetime.fromisoformat(candle['timestamp'])
        except:
            return False
        
        # Check numeric fields
        numeric_fields = ['open', 'high', 'low', 'close', 'volume', 'turnover']
        for field in numeric_fields:
            try:
                float(candle[field])
            except:
                return False
        
        # Check logical consistency (high >= low, etc.)
        try:
            open_price = float(candle['open'])
            high_price = float(candle['high'])
            low_price = float(candle['low'])
            close_price = float(candle['close'])
            
            if high_price < low_price:
                return False
            if high_price < open_price or high_price < close_price:
                return False
            if low_price > open_price or low_price > close_price:
                return False
        except:
            return False
        
        return True

    async def fetch_and_save_simple(self, symbol: str, timeframe: str, start_time: datetime, end_time: datetime) -> bool:
        """Fetch and save data for a single symbol and timeframe"""
        # Check if we already have valid data
        is_valid, reason = self._validate_existing_file(symbol, timeframe, start_time, end_time)
        if is_valid:
            self.fetch_stats['skipped_files'] += 1
            return True
        
        # Fetch data from API
        url = f"{self.config.API_BASE_URL}/v5/market/kline"
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": timeframe,
            "start": int(start_time.timestamp() * 1000),
            "end": int(end_time.timestamp() * 1000),
            "limit": 1000  # Max limit per request
        }
        
        max_retries = 5  # Increased from 3 to 5
        retry_delay = 2  # Increased from 1 to 2 seconds
        
        for attempt in range(max_retries):
            try:
                # Add a delay before each request to avoid rate limiting
                if attempt > 0:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                
                # Add a small random jitter to avoid synchronized requests
                jitter = 0.1 + (random.random() * 0.2)  # Random delay between 0.1 and 0.3 seconds
                await asyncio.sleep(jitter)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('retCode') == 0:
                                # Process the data
                                candles = data['result']['list']
                                if not candles:
                                    print(f"No data returned for {symbol} {timeframe}")
                                    return False
                                
                                # Convert to our format
                                processed_data = []
                                for candle in candles:
                                    processed_candle = {
                                        'timestamp': datetime.fromtimestamp(int(candle[0])/1000).isoformat(),
                                        'open': candle[1],
                                        'high': candle[2],
                                        'low': candle[3],
                                        'close': candle[4],
                                        'volume': candle[5],
                                        'turnover': candle[6]
                                    }
                                    processed_data.append(processed_candle)
                                
                                # Sort by timestamp (newest first)
                                processed_data.sort(key=lambda x: x['timestamp'], reverse=True)
                                
                                # Limit to 50 entries if configured
                                if self.config.LIMIT_TO_50_ENTRIES and len(processed_data) > 50:
                                    processed_data = processed_data[:50]
                                
                                # Save to CSV
                                filename = os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")
                                fieldnames = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
                                
                                # Use async file writing
                                await self._write_csv_async(filename, fieldnames, processed_data)
                                
                                self.fetch_stats['total_candles_fetched'] += len(processed_data)
                                return True
                            else:
                                print(f"API Error for {symbol} {timeframe}: {data.get('retMsg')}")
                                return False
                        elif response.status == 403:
                            print(f"Rate limited or forbidden for {symbol} {timeframe} (attempt {attempt + 1}/{max_retries})")
                            if attempt == max_retries - 1:
                                print(f"Max retries reached for {symbol} {timeframe}, skipping...")
                                return False
                            # Continue to next retry
                        else:
                            print(f"HTTP Error {response.status} for {symbol} {timeframe}")
                            return False
            except Exception as e:
                print(f"Exception fetching {symbol} {timeframe} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return False
        
        return False

    async def _write_csv_async(self, filename: str, fieldnames: List[str], data: List[Dict]):
        """Write data to CSV file asynchronously"""
        # Use asyncio.to_thread to avoid blocking the event loop
        await asyncio.to_thread(self._write_csv_sync, filename, fieldnames, data)
    
    def _write_csv_sync(self, filename: str, fieldnames: List[str], data: List[Dict]):
        """Synchronous CSV writer (runs in a separate thread)"""
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    async def fetch_all_data(self, symbols: List[str], timeframes: List[str], days: int) -> Dict[str, Dict[str, List[Dict]]]:
        """Fetch all data for specified symbols and timeframes"""
        # Calculate date range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # Initialize result structure
        result = {symbol: {timeframe: [] for timeframe in timeframes} for symbol in symbols}
        
        # Create tasks for parallel data fetching
        tasks = []
        for symbol in symbols:
            for timeframe in timeframes:
                task = asyncio.create_task(
                    self.fetch_and_save_simple(symbol, timeframe, start_time, end_time)
                )
                tasks.append((symbol, timeframe, task))
        
        # Wait for all tasks to complete
        for symbol, timeframe, task in tasks:
            success = await task
            if success:
                # Read the saved data
                filename = os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")
                if os.path.exists(filename):
                    with open(filename, 'r') as f:
                        reader = csv.DictReader(f)
                        result[symbol][timeframe] = list(reader)
        
        return result

    def print_performance_stats(self):
        """Print performance statistics"""
        if not self.fetch_stats['start_time'] or not self.fetch_stats['end_time']:
            print("No performance data available")
            return
        
        total_duration = self.fetch_stats['end_time'] - self.fetch_stats['start_time']
        
        print("\n" + "="*60)
        print("PERFORMANCE STATISTICS")
        print("="*60)
        print(f"Total duration: {total_duration:.2f} seconds")
        print(f"Total requests: {self.fetch_stats['total_requests']}")
        print(f"Successful requests: {self.fetch_stats['successful_requests']}")
        print(f"Failed requests: {self.fetch_stats['failed_requests']}")
        print(f"Total candles fetched: {self.fetch_stats['total_candles_fetched']}")
        print(f"Skipped files: {self.fetch_stats['skipped_files']}")
        print(f"Refetched files: {self.fetch_stats['refetched_files']}")
        
        if self.fetch_stats['total_requests'] > 0:
            success_rate = (self.fetch_stats['successful_requests'] / self.fetch_stats['total_requests']) * 100
            print(f"Success rate: {success_rate:.2f}%")
        
        if self.fetch_stats['symbols_timeframes']:
            print("\nPer-symbol/timeframe statistics:")
            for key, stats in self.fetch_stats['symbols_timeframes'].items():
                symbol, timeframe = key.split('_')
                duration = stats['end_time'] - stats['start_time']
                print(f"  {symbol} {timeframe}: {stats['candles_fetched']} candles in {duration:.2f}s")
        
        print("="*60)