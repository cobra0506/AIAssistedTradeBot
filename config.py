import os

class DataCollectionConfig:
    # API settings
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
    BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
    API_BASE_URL = 'https://api.bybit.com'
    
    # Data settings
    SYMBOLS = ['BTCUSDT']#, 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    TIMEFRAMES = ['1', '5', '15']  # Bybit uses numbers for timeframes
    DATA_DIR = 'data'
    
    # Data collection mode
    # True = Keep only last 50 entries (for simple strategy testing)
    # False = Get full historical data (for AI training)
    LIMIT_TO_50_ENTRIES = True
    
    # Fetch all symbols from Bybit
    # True = Get all available symbols from Bybit
    # False = Use only symbols in SYMBOLS list
    FETCH_ALL_SYMBOLS = False
    
    # Automatic integrity check after data collection
    # True = Always run integrity check after fetching data
    # False = Skip integrity check (unless manually requested)
    # CHANGED: Default to False to avoid breaking existing functionality
    RUN_INTEGRITY_CHECK = True
    
    # Fetch settings
    DAYS_TO_FETCH = 7
    MAX_WORKERS = 10  # For parallel processing
    REQUEST_TIMEOUT = 10  # seconds
    RATE_LIMIT_DELAY = 0.1  # seconds between requests
    
    # Performance settings
    SHOW_DETAILED_TIMING = True
    SHOW_PERFORMANCE_STATS = True