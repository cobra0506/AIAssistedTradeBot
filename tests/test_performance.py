# test_performance.py
import pytest
import asyncio
import tempfile
import time
import psutil
from unittest.mock import Mock, patch, AsyncMock
from shared_modules.data_collection.hybrid_system import HybridTradingSystem
from shared_modules.data_collection.config import DataCollectionConfig

class TestPerformance:
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def config(self, temp_dir):
        config = Mock(spec=DataCollectionConfig)
        config.DATA_DIR = temp_dir
        config.SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
        config.TIMEFRAMES = ['1', '5', '15']
        config.DAYS_TO_FETCH = 30
        config.ENABLE_WEBSOCKET = True
        config.FETCH_ALL_SYMBOLS = False
        config.LIMIT_TO_50_ENTRIES = False
        return config
    
    @pytest.mark.asyncio
    async def test_historical_fetch_performance(self, config):
        """Test historical data fetching performance"""
        hybrid_system = HybridTradingSystem(config)
        
        # Mock data for 30 days * 24 hours * 60 minutes = 43,200 candles per timeframe
        mock_data = []
        for i in range(43200):
            mock_data.append({
                'timestamp': 1609459200000 + i * 60000,
                'open': 29000.0 + (i % 1000),
                'high': 29500.0 + (i % 1000),
                'low': 28900.0 + (i % 1000),
                'close': 29400.0 + (i % 1000),
                'volume': 1000.0 + (i % 500)
            })
        
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch:
            mock_fetch.return_value = mock_data
            
            # Monitor memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Time the operation
            start_time = time.time()
            
            await hybrid_system.collect_historical_data()
            
            end_time = time.time()
            duration = end_time - start_time
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"Historical fetch took {duration:.2f} seconds")
            print(f"Memory increase: {memory_increase:.2f} MB")
            
            # Performance assertions (adjust based on your requirements)
            assert duration < 60.0  # Should complete within 60 seconds
            assert memory_increase < 500  # Memory increase should be reasonable
    
    @pytest.mark.asyncio
    async def test_websocket_performance(self, config):
        """Test WebSocket performance under high message load"""
        hybrid_system = HybridTradingSystem(config)
        
        message_count = 0
        start_time = None
        
        async def message_callback(symbol, timeframe, candle):
            nonlocal message_count
            message_count += 1
            
            if message_count == 1:
                nonlocal start_time
                start_time = time.time()
        
        # Register callback
        hybrid_system.websocket_handler.callbacks.append(message_callback)
        
        with patch.object(hybrid_system.websocket_handler, 'connect') as mock_connect:
            mock_connect.return_value = AsyncMock()
            
            # Start WebSocket
            task = asyncio.create_task(hybrid_system.start_websocket())
            
            # Simulate high message load
            messages_to_send = 1000
            for i in range(messages_to_send):
                candle = {
                    'timestamp': 1609459200000 + i * 1000,  # 1 second intervals
                    'datetime': f'2021-01-01 00:00:{i:02d}',
                    'open': 29000.0 + i,
                    'high': 29500.0 + i,
                    'low': 28900.0 + i,
                    'close': 29400.0 + i,
                    'volume': 1000.0 + i
                }
                
                await hybrid_system.websocket_handler._process_candle_data(
                    'BTCUSDT', '1', candle
                )
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.001)
            
            # Wait for processing to complete
            await asyncio.sleep(0.1)
            
            # Stop WebSocket
            hybrid_system.websocket_handler.running = False
            await task
            
            # Calculate performance metrics
            end_time = time.time()
            duration = end_time - start_time if start_time else 0
            messages_per_second = message_count / duration if duration > 0 else 0
            
            print(f"Processed {message_count} messages in {duration:.2f} seconds")
            print(f"Messages per second: {messages_per_second:.2f}")
            
            # Performance assertions
            assert message_count == messages_to_send
            assert messages_per_second > 100  # Should handle at least 100 messages/second
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, config):
        """Test performance with concurrent historical and WebSocket operations"""
        hybrid_system = HybridTradingSystem(config)
        
        # Mock historical data
        mock_historical_data = []
        for i in range(1000):
            mock_historical_data.append({
                'timestamp': 1609459200000 + i * 60000,
                'open': 29000.0 + i,
                'high': 29500.0 + i,
                'low': 28900.0 + i,
                'close': 29400.0 + i,
                'volume': 1000.0 + i
            })
        
        websocket_messages = 0
        
        async def websocket_callback(symbol, timeframe, candle):
            nonlocal websocket_messages
            websocket_messages += 1
        
        hybrid_system.websocket_handler.callbacks.append(websocket_callback)
        
        # Start both operations concurrently
        with patch.object(hybrid_system.data_fetcher, 'fetch_historical_data_fast') as mock_fetch, \
             patch.object(hybrid_system.websocket_handler, 'connect') as mock_connect:
            
            mock_fetch.return_value = mock_historical_data
            mock_connect.return_value = AsyncMock()
            
            start_time = time.time()
            
            # Start both operations
            historical_task = asyncio.create_task(hybrid_system.collect_historical_data())
            websocket_task = asyncio.create_task(hybrid_system.start_websocket())
            
            # Simulate WebSocket messages while historical fetch runs
            for i in range(100):
                candle = {
                    'timestamp': 1609459200000 + i * 60000,
                    'datetime': f'2021-01-01 {i//60:02d}:{i%60:02d}:00',
                    'open': 29000.0 + i,
                    'high': 29500.0 + i,
                    'low': 28900.0 + i,
                    'close': 29400.0 + i,
                    'volume': 1000.0 + i
                }
                
                await hybrid_system.websocket_handler._process_candle_data(
                    'BTCUSDT', '1', candle
                )
                
                await asyncio.sleep(0.01)
            
            # Wait for completion
            await historical_task
            hybrid_system.websocket_handler.running = False
            await websocket_task
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"Concurrent operations took {duration:.2f} seconds")
            print(f"Processed {websocket_messages} WebSocket messages concurrently")
            
            # Verify both operations completed successfully
            assert duration < 30.0  # Should complete within 30 seconds
            assert websocket_messages == 100
            
            # Verify files were created
            assert (config.DATA_DIR / 'BTCUSDT_1.csv').exists()