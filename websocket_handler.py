import websocket
import json
import threading
import time
from datetime import datetime
from typing import Dict, Any, List
from .config import DataCollectionConfig
from .csv_manager import CSVManager

class WebSocketHandler:
    def __init__(self, config: DataCollectionConfig, csv_manager: CSVManager):
        self.config = config
        self.csv_manager = csv_manager
        self.ws = None
        self.running = False
        self.current_candles = {}  # Store incomplete candles
        self.lock = threading.Lock()
    
    def on_message(self, ws, message):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            
            if 'topic' in data and data['topic'].startswith('kline.'):
                # Parse kline data
                topic_parts = data['topic'].split('.')
                timeframe = topic_parts[1]
                symbol = topic_parts[2]
                
                kline_data = data['data'][0]
                
                # Create candle data
                candle = {
                    'timestamp': datetime.fromtimestamp(int(kline_data['start']) / 1000).isoformat(),
                    'open': kline_data['open'],
                    'high': kline_data['high'],
                    'low': kline_data['low'],
                    'close': kline_data['close'],
                    'volume': kline_data['volume'],
                    'turnover': kline_data['turnover']
                }
                
                # Store or update candle
                key = f"{symbol}_{timeframe}"
                with self.lock:
                    if kline_data['confirm'] == '1':  # Candle closed
                        # Save completed candle
                        self.csv_manager.write_data(symbol, timeframe, [candle])
                        # Remove from current candles
                        if key in self.current_candles:
                            del self.current_candles[key]
                    else:  # Candle still forming
                        self.current_candles[key] = candle
        
        except Exception as e:
            print(f"Error processing WebSocket message: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        print(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print("WebSocket closed")
        if self.running:
            print("Reconnecting in 5 seconds...")
            time.sleep(self.config.WS_RECONNECT_DELAY)
            self.connect()
    
    def on_open(self, ws):
        """Handle WebSocket open"""
        print("WebSocket connected")
        
        # Subscribe to klines for all symbols and timeframes
        for symbol in self.config.SYMBOLS:
            for timeframe in self.config.TIMEFRAMES:
                subscribe_message = {
                    "op": "subscribe",
                    "args": [f"kline.{timeframe}.{symbol}"]
                }
                ws.send(json.dumps(subscribe_message))
    
    def connect(self):
        """Connect to WebSocket"""
        self.ws = websocket.WebSocketApp(
            self.config.WS_URL,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        
        # Run WebSocket in a separate thread
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
    
    def start(self):
        """Start WebSocket handler"""
        self.running = True
        self.connect()
    
    def stop(self):
        """Stop WebSocket handler"""
        self.running = False
        if self.ws:
            self.ws.close()