import os
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
                        
                        # Filter symbols (like RedoneTradeBot)
                        symbols = [
                            item['symbol'] for item in items
                            if not any(excl in item['symbol'] for excl in excluded_symbols)
                            and "-" not in item['symbol']
                            and not item['symbol'].endswith("PERP")
                            and item['symbol'].endswith('USDT')
                            and item.get('contractType') == 'PERPETUAL'
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
        return sorted(all_symbols)
    
    def _validate_existing_file(self, symbol: str, timeframe: str, 
                               required_start: datetime, required_end: datetime) -> Tuple[bool, str]:
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
            end_tolerance = timedelta(hours=1)
            if last_timestamp < datetime.now() - end_tolerance:
                return False, f"Data ends too early: {last_timestamp}"
            
            # Check if we have enough data (rough estimate)
            expected_candles = self._calculate_expected_candles(timeframe, required_start, required_end)
            actual_candles = len(data)
            
            # Allow 10% tolerance for candle count
            if actual_candles < expected_candles * 0.9:
                return False, f"Insufficient data: {actual_candles} candles, expected ~{expected_candles}"
            
            return True, "Data is valid"
            
        except Exception as e:
            return False, f"Error validating file: {str(e)}"
    
    def _calculate_expected_candles(self, timeframe: str, start_time: datetime, end_time: datetime) -> int:
        """Calculate expected number of candles for a timeframe"""
        # Convert timeframe to minutes
        timeframe_minutes = {
            '1': 1,
            '5': 5,
            '15': 15,
            '60': 60,
            '240': 240,
            '1440': 1440
        }.get(timeframe, 1)
        
        # Calculate total minutes and divide by timeframe
        total_minutes = (end_time - start_time).total_seconds() / 60
        return int(total_minutes / timeframe_minutes)
    
    def fetch_historical_klines_simple(self, symbol: str, timeframe: str, 
                                     start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Simple and reliable historical klines fetching"""
        url = f"{self.config.API_BASE_URL}/v5/market/kline"
        
        # Check if we already have good data
        is_valid, reason = self._validate_existing_file(symbol, timeframe, start_time, end_time)
        if is_valid:
            self.fetch_stats['skipped_files'] += 1
            print(f"  ✓ {symbol} {timeframe}: Skipping - {reason}")
            return []
        
        if os.path.exists(os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")):
            self.fetch_stats['refetched_files'] += 1
            print(f"  ↻ {symbol} {timeframe}: Refetching - {reason}")
        
        all_data = []
        current_end_time = end_time
        batch_count = 0
        max_batches = 100  # Safety limit
        
        print(f"  Fetching {symbol} {timeframe} from {start_time} to {end_time}")
        
        try:
            while batch_count < max_batches:
                batch_count += 1
                
                # Calculate start time for this batch (work backwards)
                timeframe_minutes = int(timeframe)  # 1, 5, 15, etc.
                candles_per_batch = 1000
                batch_duration_minutes = candles_per_batch * timeframe_minutes
                batch_duration = timedelta(minutes=batch_duration_minutes)
                
                current_start_time = max(current_end_time - batch_duration, start_time)
                
                # Format parameters for Bybit API
                params = {
                    'category': 'linear',
                    'symbol': symbol,
                    'interval': timeframe,
                    'start': int(current_start_time.timestamp() * 1000),
                    'end': int(current_end_time.timestamp() * 1000),
                    'limit': 1000
                }
                
                key = f"{symbol}_{timeframe}"
                start_time_req = time.time()
                
                try:
                    self.fetch_stats['total_requests'] += 1
                    response = self.session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if data.get('retCode') == 0:
                            klines = data['result']['list']
                            
                            if not klines:
                                print(f"    No more data available")
                                break
                            
                            # Process candles (exclude open candle)
                            batch_klines = []
                            for kline in klines[:-1]:  # Exclude the last (open) candle
                                candle = {
                                    'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000).isoformat(),
                                    'open': kline[1],
                                    'high': kline[2],
                                    'low': kline[3],
                                    'close': kline[4],
                                    'volume': kline[5],
                                    'turnover': kline[6]
                                }
                                
                                if self._validate_candle(candle):
                                    batch_klines.append(candle)
                                else:
                                    print(f"    Skipping invalid candle: {candle}")
                            
                            # Update stats
                            fetch_time = time.time() - start_time_req
                            self.fetch_stats['successful_requests'] += 1
                            self.fetch_stats['total_time'] += fetch_time
                            self.fetch_stats['total_candles_fetched'] += len(batch_klines)
                            
                            # Show batch info
                            if batch_klines:
                                first_ts = datetime.fromtimestamp(int(klines[0][0]) / 1000)
                                last_ts = datetime.fromtimestamp(int(klines[-2][0]) / 1000)  # -2 because we excluded last
                                print(f"    Batch {batch_count}: {len(batch_klines)} candles ({first_ts} to {last_ts})")
                            
                            # Add to all data (we'll sort later)
                            all_data.extend(batch_klines)
                            
                            # Move to next batch (work backwards)
                            current_end_time = current_start_time
                            
                            # Check if we've reached our start time
                            if current_start_time <= start_time:
                                print(f"    Reached start time, stopping")
                                break
                            
                            # Small delay every few batches
                            if batch_count % 5 == 0:
                                time.sleep(self.config.RATE_LIMIT_DELAY)
                            
                        else:
                            self.fetch_stats['failed_requests'] += 1
                            print(f"    API Error: {data.get('retMsg')}")
                            break
                    else:
                        self.fetch_stats['failed_requests'] += 1
                        print(f"    HTTP Error: {response.status_code}")
                        break
                
                except Exception as e:
                    self.fetch_stats['failed_requests'] += 1
                    print(f"    Exception: {e}")
                    break
            
            if batch_count >= max_batches:
                print(f"    WARNING: Reached maximum batch limit ({max_batches})")
            
            # Sort all data by timestamp (since we worked backwards)
            all_data.sort(key=lambda x: x['timestamp'])
            
            # Remove duplicates
            unique_data = []
            seen_timestamps = set()
            for candle in all_data:
                if candle['timestamp'] not in seen_timestamps:
                    unique_data.append(candle)
                    seen_timestamps.add(candle['timestamp'])
            
            print(f"  ✓ {symbol} {timeframe}: {len(unique_data)} unique candles in {batch_count} batches")
            return unique_data
            
        except Exception as e:
            print(f"  ✗ {symbol} {timeframe}: Failed - {e}")
            return []
    
    def _validate_candle(self, candle: Dict[str, Any]) -> bool:
        """Validate candle data"""
        try:
            required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            if not all(field in candle for field in required_fields):
                return False
            
            open_price = float(candle['open'])
            high_price = float(candle['high'])
            low_price = float(candle['low'])
            close_price = float(candle['close'])
            volume = float(candle['volume'])
            
            if not (low_price <= high_price and 
                    low_price <= open_price <= high_price and 
                    low_price <= close_price <= high_price):
                return False
            
            if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0 or volume < 0:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def save_to_csv_batched(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]):
        """Save data to CSV with batched writing for better performance"""
        if not data:
            return
        
        filename = os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")
        
        try:
            # Write all data at once (faster than appending)
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            mode_text = "Limited to 50 entries" if self.config.LIMIT_TO_50_ENTRIES else "Full historical data"
            if self.config.LIMIT_TO_50_ENTRIES:
                # If limiting, keep only last 50 entries
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    all_data = list(reader)
                
                limited_data = all_data[-50:]
                
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=limited_data[0].keys())
                    writer.writeheader()
                    writer.writerows(limited_data)
                
                print(f"Saved {len(limited_data)} records to {filename} ({mode_text})")
            else:
                print(f"Saved {len(data)} records to {filename} ({mode_text})")
                
        except Exception as e:
            print(f"Error writing data for {symbol} {timeframe}: {e}")
    
    def fetch_all_data(self, days_back: int = None):
        """Fetch historical data for all symbols and timeframes with optimizations"""
        if days_back is None:
            days_back = self.config.DAYS_TO_FETCH
        
        self.fetch_stats['start_time'] = time.time()
        start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        symbols_to_fetch = self.all_symbols if self.config.FETCH_ALL_SYMBOLS else self.config.SYMBOLS
        mode_text = "All symbols" if self.config.FETCH_ALL_SYMBOLS else "Configured symbols"
        limit_text = "Limited to 50 entries" if self.config.LIMIT_TO_50_ENTRIES else "Full historical data"
        
        print(f"{'='*60}")
        print(f"SIMPLE BACKWARD PAGINATION DATA COLLECTOR")
        print(f"{'='*60}")
        print(f"Start time: {start_datetime}")
        print(f"Days: {days_back} ({start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')})")
        print(f"Symbols: {mode_text} ({len(symbols_to_fetch)})")
        print(f"Timeframes: {self.config.TIMEFRAMES}")
        print(f"Mode: {limit_text}")
        print(f"Workers: {self.config.MAX_WORKERS}")
        print(f"{'='*60}")
        
        # Use ThreadPoolExecutor with optimized settings
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            # Submit all tasks
            future_to_symbol_tf = {}
            for symbol in symbols_to_fetch:
                for timeframe in self.config.TIMEFRAMES:
                    future = executor.submit(
                        self.fetch_and_save_simple,
                        symbol, timeframe, start_time, end_time
                    )
                    future_to_symbol_tf[future] = (symbol, timeframe)
            
            # Process results with progress tracking
            completed = 0
            total_tasks = len(future_to_symbol_tf)
            last_progress_time = time.time()
            
            for future in concurrent.futures.as_completed(future_to_symbol_tf):
                symbol, timeframe = future_to_symbol_tf[future]
                completed += 1
                
                try:
                    success = future.result()
                    # Show progress every 5 seconds or every 10 tasks
                    current_time = time.time()
                    if current_time - last_progress_time > 5 or completed % 10 == 0:
                        progress = (completed / total_tasks) * 100
                        print(f"Progress: {completed}/{total_tasks} ({progress:.1f}%)")
                        last_progress_time = current_time
                except Exception as e:
                    print(f"Error processing {symbol} {timeframe}: {e}")
        
        # Final stats
        self.fetch_stats['end_time'] = time.time()
        total_duration = self.fetch_stats['end_time'] - self.fetch_stats['start_time']
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n{'='*60}")
        print(f"COMPLETED")
        print(f"{'='*60}")
        print(f"End time: {end_datetime}")
        print(f"Total duration: {total_duration:.2f} seconds")
        print(f"Candles fetched: {self.fetch_stats['total_candles_fetched']}")
        print(f"Files skipped: {self.fetch_stats['skipped_files']}")
        print(f"Files refetched: {self.fetch_stats['refetched_files']}")
        print(f"Average per task: {total_duration/total_tasks:.2f} seconds")
        print(f"{'='*60}")
    
    def fetch_and_save_simple(self, symbol: str, timeframe: str, 
                             start_time: datetime, end_time: datetime) -> bool:
        """Fetch and save using simple backward pagination"""
        try:
            data = self.fetch_historical_klines_simple(symbol, timeframe, start_time, end_time)
            if data:
                self.save_to_csv_batched(symbol, timeframe, data)
                return True
            return False
        except Exception as e:
            print(f"Error in fetch_and_save for {symbol} {timeframe}: {e}")
            return False


'''import os
import csv
import time
import requests
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Any
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
            'total_candles_fetched': 0
        }
        
        # Get all symbols if enabled
        if self.config.FETCH_ALL_SYMBOLS:
            self.all_symbols = self._get_all_symbols()
            print(f"Found {len(self.all_symbols)} symbols from Bybit")
        else:
            self.all_symbols = self.config.SYMBOLS
    
    def _get_all_symbols(self) -> List[str]:
        """Get all available linear symbols from Bybit with pagination (like RedoneTradeBot)"""
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
                        
                        # Filter symbols (like RedoneTradeBot)
                        symbols = [
                            item['symbol'] for item in items
                            if not any(excl in item['symbol'] for excl in excluded_symbols)
                            and "-" not in item['symbol']
                            and not item['symbol'].endswith("PERP")
                            and item['symbol'].endswith('USDT')
                            and item.get('contractType') == 'PERPETUAL'
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
                
                # Small delay to avoid rate limiting
                time.sleep(self.config.RATE_LIMIT_DELAY)
                
            except Exception as e:
                print(f"Exception fetching symbols: {e}")
                break
        
        print(f"Fetched {len(all_symbols)} perpetual symbols")
        return sorted(all_symbols)
    
    def fetch_historical_klines_forward_paginated(self, symbol: str, timeframe: str, 
                                               start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch historical klines data using forward pagination (like RedoneTradeBot)"""
        url = f"{self.config.API_BASE_URL}/v5/market/kline"
        
        all_data = []
        current_start_time = int(start_time.timestamp() * 1000)  # Convert to milliseconds
        end_time_ms = int(end_time.timestamp() * 1000)
        batch_count = 0
        
        print(f"  Forward paginating for {symbol} {timeframe} from {start_time} to {end_time}")
        
        while True:
            batch_count += 1
            print(f"    Fetching batch {batch_count} from {datetime.fromtimestamp(current_start_time/1000)}...")
            
            params = {
                'category': 'linear',
                'symbol': symbol,
                'interval': timeframe,
                'start': current_start_time,
                'limit': 1000  # Maximum allowed by Bybit
            }
            
            # Add end time if we're getting close to it
            if current_start_time + (1000 * 60 * 60 * 24) > end_time_ms:  # Within 1 day of end
                params['end'] = end_time_ms
            
            key = f"{symbol}_{timeframe}"
            start_time_req = time.time()
            
            try:
                self.fetch_stats['total_requests'] += 1
                
                response = self.session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('retCode') == 0:
                        klines = data['result']['list']
                        
                        if not klines:
                            print(f"    No more data available for {symbol} {timeframe}")
                            break
                        
                        # Format the klines (exclude the last open candle like RedoneTradeBot)
                        batch_klines = []
                        for kline in klines[:-1]:  # Exclude open candle
                            candle = {
                                'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000).isoformat(),
                                'open': kline[1],
                                'high': kline[2],
                                'low': kline[3],
                                'close': kline[4],
                                'volume': kline[5],
                                'turnover': kline[6]
                            }
                            
                            # Validate candle (like RedoneTradeBot)
                            if self._validate_candle(candle):
                                batch_klines.append(candle)
                            else:
                                print(f"    Skipping invalid candle for {symbol} {timeframe}: {candle}")
                        
                        # Update stats
                        fetch_time = time.time() - start_time_req
                        self.fetch_stats['successful_requests'] += 1
                        self.fetch_stats['total_time'] += fetch_time
                        self.fetch_stats['total_candles_fetched'] += len(batch_klines)
                        
                        if key not in self.fetch_stats['symbols_timeframes']:
                            self.fetch_stats['symbols_timeframes'][key] = {
                                'count': 0,
                                'total_time': 0,
                                'success_count': 0,
                                'candles_fetched': 0
                            }
                        
                        self.fetch_stats['symbols_timeframes'][key]['count'] += 1
                        self.fetch_stats['symbols_timeframes'][key]['total_time'] += fetch_time
                        self.fetch_stats['symbols_timeframes'][key]['success_count'] += 1
                        self.fetch_stats['symbols_timeframes'][key]['candles_fetched'] += len(batch_klines)
                        
                        # Add batch to all data
                        all_data.extend(batch_klines)
                        
                        print(f"    Got {len(batch_klines)} valid candles")
                        
                        # Check if we should stop (like RedoneTradeBot)
                        if len(klines) < 1000:
                            print(f"    Last batch received, stopping pagination")
                            break
                        
                        # Move forward safely to avoid duplicates (like RedoneTradeBot)
                        current_start_time = int(klines[-1][0]) + 1
                        
                        # Check if we've reached the end time
                        if current_start_time >= end_time_ms:
                            print(f"    Reached end time, stopping pagination")
                            break
                        
                        # Small delay to avoid rate limiting
                        time.sleep(self.config.RATE_LIMIT_DELAY)
                        
                    else:
                        self.fetch_stats['failed_requests'] += 1
                        print(f"    API Error for {symbol} {timeframe}: {data.get('retMsg')}")
                        break
                else:
                    self.fetch_stats['failed_requests'] += 1
                    print(f"    HTTP Error for {symbol} {timeframe}: {response.status_code}")
                    break
            
            except Exception as e:
                self.fetch_stats['failed_requests'] += 1
                print(f"    Exception for {symbol} {timeframe}: {e}")
                break
        
        # De-duplicate and sort by timestamp (like RedoneTradeBot)
        unique_data = {candle['timestamp']: candle for candle in all_data}
        sorted_data = sorted(unique_data.values(), key=lambda x: x['timestamp'])
        
        print(f"  Completed {symbol} {timeframe}: {len(sorted_data)} unique candles in {batch_count} batches")
        
        return sorted_data
    
    def _validate_candle(self, candle: Dict[str, Any]) -> bool:
        """Validate candle data (like RedoneTradeBot)"""
        try:
            # Check required fields
            required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
            if not all(field in candle for field in required_fields):
                return False
            
            # Check price relationships
            open_price = float(candle['open'])
            high_price = float(candle['high'])
            low_price = float(candle['low'])
            close_price = float(candle['close'])
            volume = float(candle['volume'])
            
            # Validate price relationships
            if not (low_price <= high_price and 
                    low_price <= open_price <= high_price and 
                    low_price <= close_price <= high_price):
                return False
            
            # Validate positive values
            if open_price <= 0 or high_price <= 0 or low_price <= 0 or close_price <= 0 or volume < 0:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def fetch_historical_klines(self, symbol: str, timeframe: str, 
                               start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch historical klines data from Bybit (uses forward pagination like RedoneTradeBot)"""
        return self.fetch_historical_klines_forward_paginated(symbol, timeframe, start_time, end_time)
    
    def save_to_csv(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]):
        """Save data to CSV file with optional size limit"""
        filename = os.path.join(self.config.DATA_DIR, f"{symbol}_{timeframe}.csv")
        
        # Read existing data
        existing_data = []
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    existing_data = list(reader)
            except Exception as e:
                print(f"Error reading existing data for {symbol} {timeframe}: {e}")
        
        # Combine and sort by timestamp
        all_data = existing_data + data
        all_data.sort(key=lambda x: x['timestamp'])
        
        # Remove duplicates
        unique_data = []
        seen_timestamps = set()
        for row in all_data:
            if row['timestamp'] not in seen_timestamps:
                unique_data.append(row)
                seen_timestamps.add(row['timestamp'])
        
        # Apply size limit if enabled
        if self.config.LIMIT_TO_50_ENTRIES:
            final_data = unique_data[-50:]  # Keep only last 50 entries
        else:
            final_data = unique_data  # Keep all data
        
        # Write to file
        if final_data:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=final_data[0].keys())
                    writer.writeheader()
                    writer.writerows(final_data)
                
                mode_text = "Limited to 50 entries" if self.config.LIMIT_TO_50_ENTRIES else "Full historical data"
                print(f"Saved {len(final_data)} records to {filename} ({mode_text})")
            except Exception as e:
                print(f"Error writing data for {symbol} {timeframe}: {e}")
    
    def fetch_all_data(self, days_back: int = None):
        """Fetch historical data for all symbols and timeframes using parallel processing"""
        if days_back is None:
            days_back = self.config.DAYS_TO_FETCH
        
        # Start timing
        self.fetch_stats['start_time'] = time.time()
        start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        # Show configuration
        symbols_to_fetch = self.all_symbols if self.config.FETCH_ALL_SYMBOLS else self.config.SYMBOLS
        mode_text = "All symbols from Bybit" if self.config.FETCH_ALL_SYMBOLS else "Configured symbols"
        limit_text = "Limited to 50 entries" if self.config.LIMIT_TO_50_ENTRIES else "Full historical data"
        
        print(f"{'='*60}")
        print(f"FAST DATA COLLECTOR STARTING (RedoneTradeBot Method)")
        print(f"{'='*60}")
        print(f"Start time: {start_datetime}")
        print(f"Days to fetch: {days_back}")
        print(f"Date range: {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
        print(f"Symbols: {mode_text} ({len(symbols_to_fetch)} symbols)")
        print(f"Timeframes: {self.config.TIMEFRAMES}")
        print(f"Data mode: {limit_text}")
        print(f"Parallel workers: {self.config.MAX_WORKERS}")
        print(f"{'='*60}")
        
        # Use ThreadPoolExecutor for parallel fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            future_to_symbol_tf = {}
            
            for symbol in symbols_to_fetch:
                for timeframe in self.config.TIMEFRAMES:
                    future = executor.submit(
                        self.fetch_and_save,
                        symbol, timeframe, start_time, end_time
                    )
                    future_to_symbol_tf[future] = (symbol, timeframe)
            
            completed = 0
            total_tasks = len(future_to_symbol_tf)
            
            for future in concurrent.futures.as_completed(future_to_symbol_tf):
                symbol, timeframe = future_to_symbol_tf[future]
                completed += 1
                
                try:
                    success = future.result()
                    if success:
                        if self.config.SHOW_DETAILED_TIMING:
                            print(f"[{completed}/{total_tasks}] ✓ {symbol} {timeframe}")
                    else:
                        print(f"[{completed}/{total_tasks}] ✗ {symbol} {timeframe}")
                except Exception as e:
                    print(f"[{completed}/{total_tasks}] ✗ {symbol} {timeframe} - {e}")
        
        # End timing and calculate duration
        self.fetch_stats['end_time'] = time.time()
        total_duration = self.fetch_stats['end_time'] - self.fetch_stats['start_time']
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n{'='*60}")
        print(f"DATA COLLECTION COMPLETED")
        print(f"{'='*60}")
        print(f"End time: {end_datetime}")
        print(f"Total duration: {total_duration:.2f} seconds")
        print(f"Total candles fetched: {self.fetch_stats['total_candles_fetched']}")
        print(f"Average time per symbol/timeframe: {total_duration/total_tasks:.2f} seconds")
        
        if self.config.SHOW_PERFORMANCE_STATS:
            self.print_stats()
        
        print(f"{'='*60}")
    
    def fetch_and_save(self, symbol: str, timeframe: str, 
                      start_time: datetime, end_time: datetime) -> bool:
        """Fetch data for a single symbol/timeframe and save to CSV"""
        data = self.fetch_historical_klines(symbol, timeframe, start_time, end_time)
        
        if data:
            self.save_to_csv(symbol, timeframe, data)
            return True
        
        return False
    
    def print_stats(self):
        """Print detailed performance statistics"""
        stats = self.fetch_stats
        
        print(f"\n{'='*50}")
        print(f"DETAILED PERFORMANCE STATISTICS")
        print(f"{'='*50}")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Successful requests: {stats['successful_requests']}")
        print(f"Failed requests: {stats['failed_requests']}")
        print(f"Success rate: {stats['successful_requests']/stats['total_requests']*100:.1f}%")
        print(f"Total API time: {stats['total_time']:.2f} seconds")
        print(f"Average time per request: {stats['total_time']/stats['total_requests']:.2f} seconds")
        print(f"Total candles fetched: {stats['total_candles_fetched']}")
        print(f"Average candles per request: {stats['total_candles_fetched']/stats['successful_requests']:.1f}")
        
        if self.config.SHOW_DETAILED_TIMING:
            print(f"\n{'='*30}")
            print(f"PER SYMBOL/TIMEFRAME DETAILS")
            print(f"{'='*30}")
            
            # Sort by total candles fetched (most first)
            sorted_items = sorted(stats['symbols_timeframes'].items(), 
                                key=lambda x: x[1]['candles_fetched'], reverse=True)
            
            for key, data in sorted_items:
                success_rate = data['success_count']/data['count']*100
                avg_time = data['total_time']/data['count']
                avg_candles = data['candles_fetched']/data['success_count'] if data['success_count'] > 0 else 0
                print(f"{key}: {data['candles_fetched']} candles, {data['success_count']}/{data['count']} ({success_rate:.1f}%) - "
                      f"Avg: {avg_time:.2f}s, {avg_candles:.1f} candles/request")'''