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
        """Fetch data for single symbol/timeframe"""
        end_time = int(time.time() * 1000)
        
        # Calculate limit per request
        limit_per_request = 50 if limit_50 else 1000
        
        # If limit_50 is True, we only need to fetch the most recent 50 candles
        # So we can make a single request with a recent start time
        if limit_50:
            # Estimate how much time we need to go back to get at least 50 candles
            # This is approximate but should be sufficient
            timeframe_minutes = int(timeframe)
            if timeframe_minutes <= 1:  # 1m or similar
                start_time = end_time - (60 * 60 * 1000)  # Go back 1 hour
            elif timeframe_minutes <= 5:  # 5m or similar
                start_time = end_time - (5 * 60 * 60 * 1000)  # Go back 5 hours
            elif timeframe_minutes <= 15:  # 15m or similar
                start_time = end_time - (15 * 60 * 60 * 1000)  # Go back 15 hours
            else:
                start_time = end_time - (24 * 60 * 60 * 1000)  # Go back 1 day
        else:
            # Full historical data - go back the specified number of days
            start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
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
                    
                    # Sort by timestamp (newest first) and limit if needed
                    processed_candles.sort(key=lambda x: x['timestamp'], reverse=True)
                    
                    if limit_50 and len(processed_candles) > 50:
                        processed_candles = processed_candles[:50]
                    
                    # Store in memory
                    key = f"{symbol}_{timeframe}"
                    if key not in self.memory_data:
                        self.memory_data[key] = deque(maxlen=50 if limit_50 else 5000)
                    
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
    
    ''' async def _fetch_symbol_timeframe(self, symbol: str, timeframe: str, 
                                    days: int, limit_50: bool):
        """Fetch data for single symbol/timeframe"""
        end_time = int(time.time() * 1000)
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
        # Calculate limit
        limit = 50 if limit_50 else 1000
        
        url = f"https://api.bybit.com/v5/market/kline"
        params = {
            "category": "linear",
            "symbol": symbol,
            "interval": timeframe,
            "start": start_time,
            "end": end_time,
            "limit": limit
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()
                
                if data.get("retCode") == 0:
                    candles = data["result"]["list"]
                    
                    # Store in memory (like RedoneTradeBot)
                    key = f"{symbol}_{timeframe}"
                    if key not in self.memory_data:
                        self.memory_data[key] = deque(maxlen=limit if limit_50 else 5000)
                    
                    # Process candles in reverse order (Bybit returns newest first)
                    processed_candles = []
                    for candle in reversed(candles):  # Reverse to get chronological order
                        processed = {
                            'timestamp': int(candle[0]),
                            'open': float(candle[1]),
                            'high': float(candle[2]),
                            'low': float(candle[3]),
                            'close': float(candle[4]),
                            'volume': float(candle[5])
                        }
                        processed_candles.append(processed)
                    
                    # Add to memory storage in chronological order
                    self.memory_data[key].extend(processed_candles)
                    
                    print(f"✅ Fetched {len(processed_candles)} candles for {symbol}_{timeframe}")
                    return True
                else:
                    print(f"❌ Error fetching {symbol}/{timeframe}: {data.get('retMsg')}")
                    return False
                    
        except Exception as e:
            print(f"❌ Exception fetching {symbol}/{timeframe}: {e}")
            return False'''
    
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