import os
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
            'symbols_timeframes': {}
        }
    
    def fetch_historical_klines(self, symbol: str, timeframe: str, 
                               start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch historical klines data from Bybit"""
        url = f"{self.config.API_BASE_URL}/v5/market/kline"
        
        params = {
            'category': 'linear',
            'symbol': symbol,
            'interval': timeframe,
            'start': int(start_time.timestamp() * 1000),
            'end': int(end_time.timestamp() * 1000),
            'limit': 1000
        }
        
        key = f"{symbol}_{timeframe}"
        start_time = time.time()
        
        try:
            self.fetch_stats['total_requests'] += 1
            
            response = self.session.get(url, params=params, timeout=self.config.REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                if data['retCode'] == 0:
                    klines = data['result']['list']
                    formatted_data = []
                    
                    for kline in klines:
                        formatted_data.append({
                            'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000).isoformat(),
                            'open': kline[1],
                            'high': kline[2],
                            'low': kline[3],
                            'close': kline[4],
                            'volume': kline[5],
                            'turnover': kline[6]
                        })
                    
                    # Update stats
                    fetch_time = time.time() - start_time
                    self.fetch_stats['successful_requests'] += 1
                    self.fetch_stats['total_time'] += fetch_time
                    
                    if key not in self.fetch_stats['symbols_timeframes']:
                        self.fetch_stats['symbols_timeframes'][key] = {
                            'count': 0,
                            'total_time': 0,
                            'success_count': 0
                        }
                    
                    self.fetch_stats['symbols_timeframes'][key]['count'] += 1
                    self.fetch_stats['symbols_timeframes'][key]['total_time'] += fetch_time
                    self.fetch_stats['symbols_timeframes'][key]['success_count'] += 1
                    
                    return formatted_data
                else:
                    self.fetch_stats['failed_requests'] += 1
                    print(f"API Error for {symbol} {timeframe}: {data['retMsg']}")
            else:
                self.fetch_stats['failed_requests'] += 1
                print(f"HTTP Error for {symbol} {timeframe}: {response.status_code}")
        
        except Exception as e:
            self.fetch_stats['failed_requests'] += 1
            print(f"Exception for {symbol} {timeframe}: {e}")
        
        return []
    
    def save_to_csv(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]):
        """Save data to CSV file with size limit"""
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
        
        # Remove duplicates and limit size
        unique_data = []
        seen_timestamps = set()
        for row in all_data:
            if row['timestamp'] not in seen_timestamps:
                unique_data.append(row)
                seen_timestamps.add(row['timestamp'])
        
        final_data = unique_data[-self.config.MAX_ENTRIES:]
        
        # Write to file
        if final_data:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=final_data[0].keys())
                    writer.writeheader()
                    writer.writerows(final_data)
                
                print(f"Saved {len(final_data)} records to {filename}")
            except Exception as e:
                print(f"Error writing data for {symbol} {timeframe}: {e}")
    
    def fetch_all_data(self, days_back: int = None):
        """Fetch historical data for all symbols and timeframes using parallel processing"""
        if days_back is None:
            days_back = self.config.DAYS_TO_FETCH
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        print(f"Fetching historical data for the last {days_back} days...")
        print(f"Symbols: {self.config.SYMBOLS}")
        print(f"Timeframes: {self.config.TIMEFRAMES}")
        print(f"Using {self.config.MAX_WORKERS} parallel workers")
        
        start_fetch_time = time.time()
        
        # Use ThreadPoolExecutor for parallel fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            future_to_symbol_tf = {}
            
            for symbol in self.config.SYMBOLS:
                for timeframe in self.config.TIMEFRAMES:
                    future = executor.submit(
                        self.fetch_and_save,
                        symbol, timeframe, start_time, end_time
                    )
                    future_to_symbol_tf[future] = (symbol, timeframe)
            
            for future in concurrent.futures.as_completed(future_to_symbol_tf):
                symbol, timeframe = future_to_symbol_tf[future]
                try:
                    success = future.result()
                    if success:
                        print(f"✓ Completed {symbol} {timeframe}")
                    else:
                        print(f"✗ Failed {symbol} {timeframe}")
                except Exception as e:
                    print(f"✗ Exception for {symbol} {timeframe}: {e}")
        
        total_time = time.time() - start_fetch_time
        print(f"\nData fetching completed in {total_time:.2f} seconds")
        self.print_stats()
    
    def fetch_and_save(self, symbol: str, timeframe: str, 
                      start_time: datetime, end_time: datetime) -> bool:
        """Fetch data for a single symbol/timeframe and save to CSV"""
        data = self.fetch_historical_klines(symbol, timeframe, start_time, end_time)
        
        if data:
            self.save_to_csv(symbol, timeframe, data)
            return True
        
        return False
    
    def print_stats(self):
        """Print performance statistics"""
        stats = self.fetch_stats
        
        print("\n=== Performance Statistics ===")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Successful requests: {stats['successful_requests']}")
        print(f"Failed requests: {stats['failed_requests']}")
        print(f"Success rate: {stats['successful_requests']/stats['total_requests']*100:.1f}%")
        print(f"Total time: {stats['total_time']:.2f} seconds")
        print(f"Average time per request: {stats['total_time']/stats['total_requests']:.2f} seconds")
        
        print("\n=== Per Symbol/Timeframe ===")
        for key, data in stats['symbols_timeframes'].items():
            print(f"{key}: {data['success_count']}/{data['count']} successful, "
                  f"avg time: {data['total_time']/data['count']:.2f}s")