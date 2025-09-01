# config.py - Ensure it has these optimized settings
import os

class DataCollectionConfig:
    # API settings
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
    API_BASE_URL = 'https://api.bybit.com'
    
    # Data settings
    SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']  # Add more symbols as needed
    TIMEFRAMES = ['1', '5', '15']  # Add more timeframes as needed
    DATA_DIR = 'data'
    
    # Data collection mode
    # True = Keep only last 50 entries (for simple strategy testing)
    # False = Get full historical data (for AI training)
    LIMIT_TO_50_ENTRIES = True
    
    # Fetch all symbols from Bybit
    # True = Get all available symbols from Bybit
    # False = Use only symbols in SYMBOLS list
    FETCH_ALL_SYMBOLS = True
    
    # WebSocket settings
    # True = Start WebSocket and continue collecting live data
    # False = Only fetch historical data and exit (for AI training)
    ENABLE_WEBSOCKET = False
    
    # Automatic integrity check after data collection
    RUN_INTEGRITY_CHECK = False  # Disabled for speed
    
    # Automatic gap filling after data collection
    RUN_GAP_FILLING = False  # Disabled for speed
    
    # Fetch settings
    DAYS_TO_FETCH = 2
    MAX_WORKERS = 50  # Increased for parallel processing
    REQUEST_TIMEOUT = 10  # seconds
    RATE_LIMIT_DELAY = 0.01  # Reduced for speed
    MAX_CONCURRENT_REQUESTS = 50  # Increased for speed
    REQUEST_DELAY = 0.01  # Reduced for speed
    
    # Performance settings
    SHOW_DETAILED_TIMING = False  # Disabled for speed
    SHOW_PERFORMANCE_STATS = False  # Disabled for speed
    
    # Testing settings
    # True = Run WebSocket test to verify live data collection
    # False = Normal operation
    TEST_WEBSOCKET = False
    
    # Rate limiting settings
    MAX_RETRIES = 3  # Maximum number of retries for failed requests
    RETRY_DELAY = 1  # Initial retry delay in seconds
    
    # New settings for optimized system
    USE_MEMORY_STORAGE = True  # Use in-memory storage like RedoneTradeBot
    WRITE_TO_CSV_ON_COMPLETE = True  # Only write CSV when done

'''import os

class DataCollectionConfig:
    # API settings
    BYBIT_API_KEY = os.getenv('kKnXjxCtTGjt5z6ZCW', '')
    BYBIT_API_SECRET = os.getenv('lAQrC1lhVO3LlcdJjgql2DVULwDU8vrPLhsW', '')
    API_BASE_URL = 'https://api.bybit.com'
    
    # Data settings
    SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']  # Add more symbols as needed
    TIMEFRAMES = ['1', '5', '15']  # Add more timeframes as needed
    DATA_DIR = 'data'
    
    # Data collection mode
    # True = Keep only last 50 entries (for simple strategy testing)
    # False = Get full historical data (for AI training)
    LIMIT_TO_50_ENTRIES = True
    
    # Fetch all symbols from Bybit
    # True = Get all available symbols from Bybit
    # False = Use only symbols in SYMBOLS list
    FETCH_ALL_SYMBOLS = True
    
    # WebSocket settings
    # True = Start WebSocket and continue collecting live data
    # False = Only fetch historical data and exit (for AI training)
    ENABLE_WEBSOCKET = True
    
    # Automatic integrity check after data collection
    RUN_INTEGRITY_CHECK = True
    
    # Automatic gap filling after data collection
    RUN_GAP_FILLING = True
    
    # Fetch settings
    DAYS_TO_FETCH = 2
    MAX_WORKERS = 10  # For parallel processing
    REQUEST_TIMEOUT = 10  # seconds
    RATE_LIMIT_DELAY = 0.1  # seconds between requests
    
    # Performance settings
    SHOW_DETAILED_TIMING = True
    SHOW_PERFORMANCE_STATS = True
    
    # Testing settings
    # True = Run WebSocket test to verify live data collection
    # False = Normal operation
    TEST_WEBSOCKET = False'''