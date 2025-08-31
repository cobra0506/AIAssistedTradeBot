import os

class DataCollectionConfig:
    # API settings
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
    API_BASE_URL = 'https://api.bybit.com'
    
    # Data settings
    SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    TIMEFRAMES = ['1', '5', '15']  # Bybit uses numbers for timeframes
    DATA_DIR = 'data'
    MAX_ENTRIES = 50  # Keep only last 50 entries per symbol/timeframe
    
    # Fetch settings
    DAYS_TO_FETCH = 7
    MAX_WORKERS = 10  # For parallel processing
    REQUEST_TIMEOUT = 10  # seconds
    RATE_LIMIT_DELAY = 0.1  # seconds between requests