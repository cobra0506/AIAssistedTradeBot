import websockets
import json
import asyncio
import ssl
from datetime import datetime, timedelta
from typing import Dict, List, Any, Callable
from config import DataCollectionConfig

class WebSocketHandler:
    def __init__(self, config: DataCollectionConfig, symbols: List[str] = None):
        self.config = config
        self.ws_url = "wss://stream.bybit.com/v5/public/linear"
        self.running = False
        self.real_time_data = {}  # Store real-time data: {symbol_timeframe: [candles]}
        self.callbacks = []  # Callback functions for processing candles
        self.debug_callbacks = []  # Debug callbacks for all messages
        self.lock = asyncio.Lock()  # For thread-safe operations
        self.connection = None  # Store the connection object
        self.subscription_count = 0  # Track successful subscriptions
        
        # Use provided symbols or fall back to config symbols
        self.symbols = symbols if symbols else config.SYMBOLS

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
            
            # Print subscription summary
            print(f"Subscription summary: {self.subscription_count} subscriptions sent")
            
            # Start heartbeat task
            heartbeat_task = asyncio.create_task(self._heartbeat(connection))
            
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
            
            # Cancel heartbeat task when done
            heartbeat_task.cancel()
            
        except Exception as e:
            print(f"Error while listening: {e}")
            raise e

    async def _heartbeat(self, websocket):
        """Send periodic pings to keep the connection alive"""
        try:
            while self.running:
                # Send a ping every 30 seconds
                await asyncio.sleep(30)
                if self.running:
                    try:
                        pong_waiter = await websocket.ping()
                        await asyncio.wait_for(pong_waiter, timeout=10)
                        print("WebSocket ping successful")
                    except Exception as e:
                        print(f"Heartbeat failed: {e}")
                        break
        except asyncio.CancelledError:
            pass

    async def _subscribe_to_symbols(self, websocket):
        """Subscribe to symbols and timeframes using batch subscriptions"""
        total_subscriptions = len(self.symbols) * len(self.config.TIMEFRAMES)
        print(f"Subscribing to {total_subscriptions} symbol/timeframe combinations using batch requests...")
        
        # Create all subscription arguments
        subscription_args = []
        for symbol in self.symbols:
            for timeframe in self.config.TIMEFRAMES:
                # Bybit uses different interval names
                interval_map = {'1': '1', '5': '5', '15': '15', '60': '60', '240': '240', '1440': 'D'}
                interval = interval_map.get(timeframe, '1')
                subscription_args.append(f"kline.{interval}.{symbol}")
        
        # Split into batches to avoid overly large messages
        batch_size = 100  # Adjust based on API limits
        batches = [subscription_args[i:i + batch_size] for i in range(0, len(subscription_args), batch_size)]
        
        print(f"Created {len(batches)} batches of up to {batch_size} subscriptions each")
        
        # Send all batch subscription requests and wait for them to complete
        for i, batch in enumerate(batches):
            try:
                subscribe_msg = {
                    "op": "subscribe",
                    "args": batch
                }
                
                await websocket.send(json.dumps(subscribe_msg))
                self.subscription_count += len(batch)
                print(f"Sent batch {i+1}/{len(batches)} with {len(batch)} subscriptions ({self.subscription_count}/{total_subscriptions})")
                
                # Add a small delay between batches to avoid rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error sending batch {i+1}: {e}")
                # Continue with the next batch even if this one fails
                continue
        
        print(f"Subscription completed. Successfully sent {self.subscription_count}/{total_subscriptions} subscription requests.")
        
        # Wait a moment for subscriptions to be processed by the server
        print("Waiting for subscriptions to be processed by the server...")
        await asyncio.sleep(2)

    def _parse_timestamp(self, timestamp_value):
        """Parse timestamp from various possible formats"""
        try:
            # If it's a number (milliseconds since epoch)
            if isinstance(timestamp_value, (int, float)):
                # Check if it's in seconds or milliseconds
                if timestamp_value > 1e10:  # Likely milliseconds
                    return datetime.fromtimestamp(timestamp_value/1000).isoformat()
                else:  # Likely seconds
                    return datetime.fromtimestamp(timestamp_value).isoformat()
            # If it's something else, try to convert to string
            else:
                return str(timestamp_value)
        except Exception as e:
            print(f"Error parsing timestamp {timestamp_value}: {e}")
            return str(timestamp_value)

    async def _process_message(self, message):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            # Check if it's a kline (candlestick) message
            if 'topic' in data and data['topic'].startswith('kline.'):
                # Extract symbol and timeframe from topic
                topic_parts = data['topic'].split('.')
                timeframe = topic_parts[1]
                symbol = topic_parts[2]
                
                # Get the candle data
                if 'data' in data:
                    candle_data = data['data']
                    
                    # Handle both single candle (dict) and multiple candles (list)
                    if isinstance(candle_data, list):
                        # Process each candle in the list
                        for candle_item in candle_data:
                            await self._process_candle_data(symbol, timeframe, candle_item)
                    else:
                        # Process single candle
                        await self._process_candle_data(symbol, timeframe, candle_data)
                        
        except Exception as e:
            print(f"Error processing message: {e}")

    async def _process_candle_data(self, symbol: str, timeframe: str, candle_data: Dict):
        """Process a single candle data object"""
        try:
            candle = {
                'timestamp': self._parse_timestamp(candle_data.get('start', 0)),
                'open': candle_data.get('open', '0'),
                'high': candle_data.get('high', '0'),
                'low': candle_data.get('low', '0'),
                'close': candle_data.get('close', '0'),
                'volume': candle_data.get('volume', '0'),
                'turnover': candle_data.get('turnover', '0'),
                'confirm': candle_data.get('confirm', False)
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
            print(f"Error processing candle data: {e}")

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
        """Get real-time data for a specific symbol and timeframe"""
        key = f"{symbol}_{timeframe}"
        return self.real_time_data.get(key, [])

    def stop(self):
        """Stop the WebSocket connection"""
        self.running = False