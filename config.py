import os

class DataCollectionConfig:
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
    
    # Symbols and timeframes to track
    SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    TIMEFRAMES = ['1m', '5m', '15m']
    
    # Data storage settings
    DATA_DIR = 'data'
    MAX_ENTRIES = 50  # Keep only last 50 entries per symbol/timeframe
    
    # API settings
    API_BASE_URL = 'https://api.bybit.com'
    WS_URL = 'wss://stream.bybit.com/v5/public/linear'
    
    # Rate limiting
    API_RATE_LIMIT = 100  # requests per minute
    WS_RECONNECT_DELAY = 5  # seconds
    
    # Parallel processing
    MAX_WORKERS = 5  # for parallel symbol processing
    
    # Default settings for running without command line arguments
    DEFAULT_HISTORICAL_DAYS = 7  # Default number of days to fetch
    DEFAULT_MODE = 'both'  # Options: 'historical', 'realtime', 'both'