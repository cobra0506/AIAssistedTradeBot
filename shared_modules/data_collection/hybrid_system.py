# hybrid_system.py - Updated with fixed WebSocket handling
import asyncio
import os
import logging
from typing import Dict, List, Any
from datetime import datetime
from .config import DataCollectionConfig  # Relative import
from .optimized_data_fetcher import OptimizedDataFetcher
from .websocket_handler import WebSocketHandler
from .csv_manager import CSVManager
from .logging_utils import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

class HybridTradingSystem:
    def __init__(self, config):
        self.config = config
        self.data_fetcher = OptimizedDataFetcher(config)
        self.websocket_handler = WebSocketHandler(config)
        self.csv_manager = CSVManager(config)
        self.is_initialized = False

    async def initialize(self):
        """Initialize both fetchers"""
        if not self.is_initialized:
            await self.data_fetcher.initialize()
            self.is_initialized = True

    async def fetch_data_hybrid(self, symbols: List[str] = None, timeframes: List[str] = None,
                               days: int = None, mode: str = "full"):
        """
        mode: "full" = all historical data
              "recent" = only 50 most recent entries
              "live" = only real-time data
        """
        # Use config values if not provided
        if symbols is None:
            symbols = self.config.SYMBOLS
        if timeframes is None:
            timeframes = self.config.TIMEFRAMES
        if days is None:
            days = self.config.DAYS_TO_FETCH
            
        logger.info(f"[DEBUG] Starting data fetch in mode: {mode}")
        
        # Get symbols to use
        if self.config.FETCH_ALL_SYMBOLS:
            # Fetch all symbols from Bybit
            logger.info("[DATA] Fetching all symbols from Bybit...")
            all_symbols = await self.data_fetcher._get_all_symbols()
            symbols_to_use = all_symbols
        else:
            # Use only symbols from config
            symbols_to_use = symbols
            logger.info(f"[DATA] Using {len(symbols_to_use)} symbols from configuration")
        
        # Start WebSocket FIRST to avoid gaps between historical and live data
        # Only start if ENABLE_WEBSOCKET is True
        if self.config.ENABLE_WEBSOCKET:
            logger.info(f"[WS] Starting WebSocket for real-time updates...")
            
            # Update symbols in the WebSocket handler
            self.websocket_handler.symbols = symbols_to_use
            self.websocket_handler.config.TIMEFRAMES = timeframes
            
            # Start WebSocket in background
            ws_task = asyncio.create_task(self.websocket_handler.connect())
            
            # Wait a bit for connection to establish
            await asyncio.sleep(3)
            
            if self.websocket_handler.running:
                logger.info(f"[OK] WebSocket connected successfully")
                logger.info(f"[OK] Subscribed to {len(symbols_to_use)} symbols and {len(timeframes)} timeframes")
            else:
                logger.error(f"[FAIL] WebSocket connection failed")
        else:
            logger.info(f"[WS] WebSocket disabled (ENABLE_WEBSOCKET=False)")
        
        # Then, fetch historical data if needed
        if mode in ["full", "recent"]:
            logger.info(f"[DATA] Fetching historical data...")
            limit_50 = (mode == "recent")
            
            success = await self.data_fetcher.fetch_historical_data_fast(
                symbols_to_use, timeframes, days, limit_50
            )
            
            if success:
                logger.info(f"[OK] Historical data fetched successfully")
                # Show sample of fetched data
                self._show_sample_data(symbols_to_use[:5], timeframes)  # Show first 5 symbols
            else:
                logger.error(f"[FAIL] Failed to fetch historical data")

    def _show_sample_data(self, symbols: List[str], timeframes: List[str]):
        """Show sample of fetched data"""
        logger.info("\n[INFO] Sample of fetched historical data:")
        
        for symbol in symbols[:2]:  # Show first 2 symbols
            for timeframe in timeframes[:2]:  # Show first 2 timeframes
                key = f"{symbol}_{timeframe}"
                data = self.data_fetcher.get_memory_data().get(key, [])
                
                if data:
                    logger.info(f" {symbol}_{timeframe}: {len(data)} candles")
                    if len(data) > 0:
                        latest = data[-1]
                        # Convert timestamp to datetime
                        dt = datetime.fromtimestamp(latest['timestamp'] / 1000)
                        datetime_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                        logger.info(f" Latest: {datetime_str} - O:{latest['open']} H:{latest['high']} L:{latest['low']} C:{latest['close']}")
                else:
                    logger.info(f" {symbol}_{timeframe}: No data")

    def get_data(self, symbol: str, timeframe: str, source: str = "memory"):
        """Get data from memory or combine historical + real-time"""
        key = f"{symbol}_{timeframe}"
        
        if source == "memory":
            return list(self.data_fetcher.get_memory_data().get(key, []))
        elif source == "websocket":
            return list(self.websocket_handler.get_real_time_data(symbol, timeframe))
        elif source == "csv":
            # Read from CSV using CSV manager
            return self.csv_manager.read_csv_data(symbol, timeframe)
        else:
            # Combine both memory and real-time
            historical = list(self.data_fetcher.get_memory_data().get(key, []))
            real_time = list(self.websocket_handler.get_real_time_data(symbol, timeframe))
            return historical + real_time

    async def save_to_csv(self, directory: str = "data"):
        """Save all data to CSV using CSV manager"""
        logger.info("[SAVE] Saving all data to CSV using CSV manager...")
        
        # Get all data from memory
        memory_data = self.data_fetcher.get_memory_data()
        
        for key, candles in memory_data.items():
            if candles:
                symbol, timeframe = key.split('_')
                success = self.csv_manager.write_csv_data(symbol, timeframe, list(candles))
                
                if not success:
                    logger.error(f"[FAIL] Failed to save {key} to CSV")
        
        logger.info("[OK] CSV save completed")

    async def update_csv_with_realtime_data(self, directory: str = "data"):
        """Update CSV files with real-time data using CSV manager"""
        # Skip if WebSocket is disabled
        if not self.config.ENABLE_WEBSOCKET:
            logger.info("CSV updates skipped (ENABLE_WEBSOCKET=False)")
            return
            
        if not self.config.LIMIT_TO_50_ENTRIES:
            logger.info("CSV updates disabled (LIMIT_TO_50_ENTRIES is False)")
            return
        
        logger.info("[WS] Updating CSV files with real-time data...")
        
        # Get symbols to use
        if self.config.FETCH_ALL_SYMBOLS:
            # For WebSocket, we need to get the symbols that were actually subscribed to
            symbols_to_use = self.websocket_handler.symbols
        else:
            symbols_to_use = self.config.SYMBOLS
        
        for symbol in symbols_to_use:
            for timeframe in self.websocket_handler.config.TIMEFRAMES:
                # Get real-time data
                real_time_data = self.websocket_handler.get_real_time_data(symbol, timeframe)
                
                if real_time_data:
                    # Convert real-time data to CSV format
                    csv_candles = []
                    for candle in real_time_data:
                        csv_candle = {
                            'timestamp': candle['timestamp'],
                            'open': float(candle['open']),
                            'high': float(candle['high']),
                            'low': float(candle['low']),
                            'close': float(candle['close']),
                            'volume': float(candle['volume'])
                        }
                        csv_candles.append(csv_candle)
                    
                    # Use CSV manager to append new data
                    success = self.csv_manager.append_new_data(symbol, timeframe, csv_candles)
                    
                    if success:
                        logger.debug(f"[OK] Updated {symbol}_{timeframe} with real-time data")
                    else:
                        logger.error(f"[FAIL] Failed to update {symbol}_{timeframe} with real-time data")

    async def close(self):
        """Clean up resources"""
        await self.data_fetcher.close()

