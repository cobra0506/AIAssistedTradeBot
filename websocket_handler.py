import websockets
import json
import asyncio
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
from config import DataCollectionConfig

class WebSocketHandler:
    def __init__(self, config: DataCollectionConfig):
        self.config = config
        self.ws_url = "wss://stream.bybit.com/v5/public/linear"
        self.running = False
        self.real_time_data = {}  # Store real-time data: {symbol_timeframe: [candles]}
        self.callbacks = []  # Callback functions for processing candles
        self.debug_callbacks = []  # Debug callbacks for all messages
        self.lock = asyncio.Lock()  # For thread-safe operations
        self.connection = None  # Store the connection object
        
    async def connect(self):
        """Connect to WebSocket and start listening"""
        self.running = True
        
        # Try different connection approaches
        connection_attempts = [
            self._connect_with_ssl,
            self._connect_without_ssl
        ]
        
        for attempt in connection_attempts:
            try:
                connection = await attempt()
                if connection:
                    self.connection = connection
                    print("WebSocket connection established!")
                    await self._listen_for_messages(connection)
                    return
            except Exception as e:
                print(f"Connection attempt failed: {e}")
                await asyncio.sleep(1)
        
        # If all attempts failed
        print("All connection attempts failed.")
        await self._reconnect()
    
    async def _connect_with_ssl(self):
        """Connect with SSL verification"""
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        return await websockets.connect(
            self.ws_url,
            ssl=ssl_context,
            ping_interval=20,
            ping_timeout=60
        )
    
    async def _connect_without_ssl(self):
        """Connect without SSL verification"""
        return await websockets.connect(
            self.ws_url,
            ssl=None,
            ping_interval=20,
            ping_timeout=60
        )
    
    async def _listen_for_messages(self, connection):
        """Listen for messages on an established connection"""
        try:
            # Subscribe to all symbols and timeframes
            await self._subscribe_to_symbols(connection)
            
            # Listen for messages
            async for message in connection:
                if not self.running:
                    break
                    
                # Call debug callbacks for all messages
                for callback in self.debug_callbacks:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                    
                # Process the message
                try:
                    await self._process_message(message)
                except Exception as e:
                    print(f"Error processing message: {e}")
                
        except Exception as e:
            print(f"Error while listening: {e}")
            raise e
    
    async def _subscribe_to_symbols(self, websocket):
        """Subscribe to symbols and timeframes"""
        for symbol in self.config.SYMBOLS:
            for timeframe in self.config.TIMEFRAMES:
                # Bybit uses different interval names
                interval_map = {'1': '1', '5': '5', '15': '15', '60': '60', '240': '240', '1440': 'D'}
                interval = interval_map.get(timeframe, '1')
                
                subscribe_msg = {
                    "op": "subscribe",
                    "args": [f"kline.{interval}.{symbol}"]
                }
                
                try:
                    await websocket.send(json.dumps(subscribe_msg))
                    print(f"Subscribed to {symbol} {timeframe}m")
                    
                    # Wait for subscription confirmation
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    
                except Exception as e:
                    print(f"Error subscribing to {symbol} {timeframe}m: {e}")
    
    def _parse_timestamp(self, timestamp_value):
        """Parse timestamp from various possible formats"""
        try:
            # If it's a number (milliseconds since epoch)
            if isinstance(timestamp_value, (int, float)):
                # Check if it's in seconds or milliseconds
                if timestamp_value > 1e10:  # Likely milliseconds
                    return datetime.fromtimestamp(timestamp_value / 1000).isoformat()
                else:  # Likely seconds
                    return datetime.fromtimestamp(timestamp_value).isoformat()
            
            # If it's something else, try to convert to string
            else:
                return datetime.fromisoformat(str(timestamp_value)).isoformat()
                
        except Exception as e:
            print(f"Error parsing timestamp {timestamp_value}: {e}")
            # Fallback to current time
            return datetime.now().isoformat()
    
    async def _process_message(self, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Check if it's a kline (candle) update
            if 'topic' in data and 'kline' in data['topic']:
                # Extract symbol and timeframe from topic
                topic_parts = data['topic'].split('.')
                symbol = topic_parts[2]
                timeframe = topic_parts[1]
                
                # Map timeframe back to our format
                timeframe_map = {'1': '1', '5': '5', '15': '15', '60': '60', '240': '240', 'D': '1440'}
                timeframe = timeframe_map.get(timeframe, '1')
                
                # Process all candles in the data array
                for candle_data in data['data']:
                    # Check if this candle is confirmed
                    is_confirmed = candle_data.get('confirm', False)
                    
                    # Parse candle with robust timestamp handling
                    candle = {
                        'timestamp': self._parse_timestamp(candle_data['start']),
                        'open': candle_data['open'],
                        'high': candle_data['high'],
                        'low': candle_data['low'],
                        'close': candle_data['close'],
                        'volume': candle_data['volume'],
                        'turnover': candle_data['turnover'],
                        'confirm': is_confirmed  # Whether candle is complete
                    }
                    
                    # Store candle
                    key = f"{symbol}_{timeframe}"
                    async with self.lock:
                        if key not in self.real_time_data:
                            self.real_time_data[key] = []
                        
                        # Check if candle already exists (avoid duplicates)
                        existing_timestamps = {c['timestamp'] for c in self.real_time_data[key]}
                        if candle['timestamp'] not in existing_timestamps:
                            self.real_time_data[key].append(candle)
                            
                            # If candle is complete, trigger callbacks
                            if candle['confirm']:
                                for callback in self.callbacks:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(symbol, timeframe, candle)
                                    else:
                                        callback(symbol, timeframe, candle)
                        else:
                            # Candle already exists, check if it's now confirmed
                            existing_candle = None
                            for c in self.real_time_data[key]:
                                if c['timestamp'] == candle['timestamp']:
                                    existing_candle = c
                                    break
                            
                            if existing_candle and not existing_candle['confirm'] and candle['confirm']:
                                existing_candle['confirm'] = True
                                for callback in self.callbacks:
                                    if asyncio.iscoroutinefunction(callback):
                                        await callback(symbol, timeframe, existing_candle)
                                    else:
                                        callback(symbol, timeframe, existing_candle)
                
        except Exception as e:
            print(f"Error processing message: {e}")
    
    async def _reconnect(self):
        """Handle reconnection logic"""
        while self.running:
            try:
                print("Attempting to reconnect WebSocket...")
                await asyncio.sleep(5)  # Wait before retry
                await self.connect()
                break
            except Exception as e:
                print(f"Reconnection failed: {e}")
                await asyncio.sleep(10)
    
    def add_callback(self, callback: Callable):
        """Add callback function to process real-time candles"""
        self.callbacks.append(callback)
    
    def add_debug_callback(self, callback: Callable):
        """Add debug callback to process all messages"""
        self.debug_callbacks.append(callback)
    
    def get_real_time_data(self, symbol: str, timeframe: str) -> List[Dict]:
        """Get accumulated real-time data for a symbol/timeframe"""
        key = f"{symbol}_{timeframe}"
        return self.real_time_data.get(key, [])
    
    def stop(self):
        """Stop the WebSocket connection"""
        self.running = False
        if self.connection:
            # Properly close the connection
            if hasattr(self.connection, 'close'):
                if asyncio.iscoroutinefunction(self.connection.close):
                    asyncio.create_task(self.connection.close())
                else:
                    self.connection.close()