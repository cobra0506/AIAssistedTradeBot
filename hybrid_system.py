# hybrid_system.py - Fixed to start WebSocket first
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from config import DataCollectionConfig
from optimized_data_fetcher import OptimizedDataFetcher
from websocket_handler import WebSocketHandler

class HybridTradingSystem:
    def __init__(self, config):
        self.config = config
        self.data_fetcher = OptimizedDataFetcher(config)
        self.websocket_handler = WebSocketHandler(config)
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize both fetchers"""
        if not self.is_initialized:
            await self.data_fetcher.initialize()
            self.is_initialized = True
        
    async def fetch_data_hybrid(self, symbols: List[str], timeframes: List[str], 
                          days: int, mode: str = "full"):
        """
        mode: "full" = all historical data
            "recent" = only 50 most recent entries
            "live" = only real-time data
        """
        print(f"🔍 Starting data fetch in mode: {mode}")
        
        # Start WebSocket FIRST to avoid gaps between historical and live data
        # Start WebSocket if ENABLE_WEBSOCKET is True, regardless of mode
        if self.config.ENABLE_WEBSOCKET:
            print(f"📡 Starting WebSocket for real-time updates...")
            
            # Update symbols and timeframes in the WebSocket handler
            self.websocket_handler.symbols = symbols
            self.websocket_handler.config.TIMEFRAMES = timeframes
            
            # Start WebSocket in background
            ws_task = asyncio.create_task(self.websocket_handler.connect())
            
            # Wait a bit for connection to establish
            await asyncio.sleep(3)
            
            if self.websocket_handler.running:
                print(f"✅ WebSocket connected successfully")
                print(f"✅ Subscribed to {len(symbols)} symbols and {len(timeframes)} timeframes")
            else:
                print(f"❌ WebSocket connection failed")
        
        # Then, fetch historical data if needed
        if mode in ["full", "recent"]:
            print(f"📊 Fetching historical data...")
            limit_50 = (mode == "recent")
            success = await self.data_fetcher.fetch_historical_data_fast(
                symbols, timeframes, days, limit_50
            )
            
            if success:
                print(f"✅ Historical data fetched successfully")
                # Show sample of fetched data
                self._show_sample_data(symbols, timeframes)
            else:
                print(f"❌ Failed to fetch historical data")
    
    def _show_sample_data(self, symbols: List[str], timeframes: List[str]):
        """Show sample of fetched data"""
        print("\n📋 Sample of fetched historical data:")
        
        for symbol in symbols[:2]:  # Show first 2 symbols
            for timeframe in timeframes[:2]:  # Show first 2 timeframes
                key = f"{symbol}_{timeframe}"
                data = self.data_fetcher.get_memory_data().get(key, [])
                
                if data:
                    print(f"  {symbol}_{timeframe}: {len(data)} candles")
                    if len(data) > 0:
                        latest = data[-1]
                        # Convert timestamp to datetime
                        dt = datetime.fromtimestamp(latest['timestamp'] / 1000)
                        datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        print(f"    Latest: {datetime_str} - O:{latest['open']} H:{latest['high']} L:{latest['low']} C:{latest['close']}")
                else:
                    print(f"  {symbol}_{timeframe}: No data")
    
    def get_data(self, symbol: str, timeframe: str, source: str = "memory"):
        """Get data from memory or combine historical + real-time"""
        key = f"{symbol}_{timeframe}"
        
        if source == "memory":
            return list(self.data_fetcher.get_memory_data().get(key, []))
        elif source == "websocket":
            # Pass symbol and timeframe to get_real_time_data
            return list(self.websocket_handler.get_real_time_data(symbol, timeframe))
        else:
            # Combine both
            historical = list(self.data_fetcher.get_memory_data().get(key, []))
            real_time = list(self.websocket_handler.get_real_time_data(symbol, timeframe))
            return historical + real_time
    
    async def save_to_csv(self, directory: str = "data"):
        """Save all data to CSV"""
        await self.data_fetcher.save_to_csv(directory)
    
    async def close(self):
        """Clean up resources"""
        await self.data_fetcher.close()

    async def update_csv_with_realtime_data(self, directory: str = "data"):
        """Update CSV files with real-time data"""
        os.makedirs(directory, exist_ok=True)
        
        for symbol in self.websocket_handler.symbols:
            for timeframe in self.websocket_handler.config.TIMEFRAMES:
                key = f"{symbol}_{timeframe}"
                filename = os.path.join(directory, f"{symbol}_{timeframe}.csv")
                
                # Get real-time data
                real_time_data = self.websocket_handler.get_real_time_data(symbol, timeframe)
                
                if real_time_data:
                    # Read existing data
                    existing_data = []
                    if os.path.exists(filename):
                        with open(filename, 'r') as f:
                            reader = csv.DictReader(f)
                            existing_data = list(reader)
                    
                    # Get the latest timestamp from existing data
                    latest_timestamp = 0
                    if existing_data:
                        latest_timestamp = int(existing_data[-1]['timestamp'])
                    
                    # Filter real-time data to only include new candles
                    new_candles = [
                        candle for candle in real_time_data
                        if candle['timestamp'] > latest_timestamp
                    ]
                    
                    if new_candles:
                        # Append new candles to existing data
                        with open(filename, 'a', newline='') as f:
                            fieldnames = ['timestamp', 'datetime', 'open', 'high', 'low', 'close', 'volume']
                            writer = csv.DictWriter(f, fieldnames=fieldnames)
                            
                            for candle in new_candles:
                                # Convert timestamp to datetime
                                dt = datetime.fromtimestamp(candle['timestamp'] / 1000)
                                datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                                
                                # Create a new row with both timestamp and datetime
                                row = candle.copy()
                                row['datetime'] = datetime_str
                                writer.writerow(row)
                        
                        print(f"📡 Updated {filename} with {len(new_candles)} new candles")