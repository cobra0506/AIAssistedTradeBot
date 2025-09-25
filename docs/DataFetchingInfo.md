AI Assisted TradeBot - Phase 1 Technical Reference 
1. System Overview 
What It Is 

A complete cryptocurrency data collection system that fetches historical and real-time market data from Bybit exchange. This is Phase 1 of a larger trading bot development project. 
Core Purpose 

     Historical Data: Fetch OHLCV data for multiple cryptocurrencies and timeframes
     Real-time Data: Stream live market data via WebSocket
     Data Storage: Save data to CSV files with integrity validation
     User Interface: Professional GUI with console fallback
     

Key Capabilities 

     Fetches data for 550+ cryptocurrencies or custom symbol lists
     Supports multiple timeframes (1m, 5m, 15m, configurable)
     Real-time WebSocket connection for live data updates
     Automatic data validation and gap filling
     Configurable data retention (50 entries vs unlimited)
     Professional GUI with system monitoring
     Batch processing with rate limiting optimization
     

2. Architecture 
Core Components 
hybrid_system.py - Central Orchestrator 

     Coordinates all data collection activities
     Manages both historical fetching and real-time WebSocket
     Provides unified interface for data operations
     

optimized_data_fetcher.py - Historical Data Engine 

     Async/await based concurrent processing
     Configurable batch sizes and rate limiting
     Automatic retry with exponential backoff
     Chunked fetching for large datasets
     

websocket_handler.py - Real-time Data Stream 

     Efficient subscription to multiple symbols/timeframes
     Connection management and auto-reconnection
     Message processing and candle confirmation
     Real-time data validation and storage
     

csv_manager.py - Data Persistence 

     CSV file creation and maintenance
     Data deduplication and chronological ordering
     Configurable data retention policies
     File integrity management
     

data_integrity.py - Data Quality Assurance 

     Comprehensive data validation
     Gap detection and automatic filling
     Integrity reporting and error tracking
     

gui_monitor.py - User Interface 

     Real-time system status monitoring
     Configuration controls with checkboxes
     System resource monitoring (CPU/Memory)
     Error tracking and activity logging
     

Data Flow 
 
 
 
1
2
3
4
5
6
7
Bybit API → Optimized Data Fetcher → CSV Manager → CSV Files
    ↓
Bybit WebSocket → WebSocket Handler → CSV Manager → CSV Files
    ↓
Configuration → Hybrid System → All Components
    ↓
GUI/Console → User Interface → System Control
 
 
 
3. Configuration 
File: config.py 
Essential Settings 
python
 
 
 
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
# API Settings
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY', '')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET', '')
API_BASE_URL = 'https://api.bybit.com'

# Data Settings
SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']  # Custom symbols
TIMEFRAMES = ['1', '5', '15']               # Time intervals (minutes)
DATA_DIR = 'data'                           # CSV storage directory

# Collection Modes
LIMIT_TO_50_ENTRIES = False    # True=50 recent entries, False=all data
FETCH_ALL_SYMBOLS = True       # True=all Bybit symbols, False=config.SYMBOLS
DAYS_TO_FETCH = 100            # Historical data depth

# Real-time Data
ENABLE_WEBSOCKET = True        # Enable real-time streaming
RUN_INTEGRITY_CHECK = False   # Run data validation
RUN_GAP_FILLING = False       # Auto-fill data gaps

# Performance
BULK_BATCH_SIZE = 20          # Concurrent requests per batch
BULK_REQUEST_DELAY_MS = 10     # Delay between batches (ms)
BULK_MAX_RETRIES = 5          # Maximum retry attempts
 
 
 
Configuration Strategies 
For AI/ML Training 
python
 
 
 
1
2
3
4
LIMIT_TO_50_ENTRIES = False    # Maximum historical data
FETCH_ALL_SYMBOLS = True       # Comprehensive dataset
DAYS_TO_FETCH = 100           # Deep historical context
ENABLE_WEBSOCKET = True       # Continuous updates
 
 
 
For Strategy Testing 
python
 
 
 
1
2
3
LIMIT_TO_50_ENTRIES = True     # Focused recent data
FETCH_ALL_SYMBOLS = False      # Specific symbols only
DAYS_TO_FETCH = 7             # Recent data only
 
 
 
For Historical Analysis 
python
 
 
 
1
2
3
LIMIT_TO_50_ENTRIES = False    # Complete historical data
FETCH_ALL_SYMBOLS = True       # Full market coverage
ENABLE_WEBSOCKET = False      # No real-time needed
 
 
 
4. Data Storage Format 
File Structure 
 
 
 
1
2
3
4
5
6
7
data/
├── BTCUSDT_1.csv      # 1-minute BTC data
├── BTCUSDT_5.csv      # 5-minute BTC data
├── BTCUSDT_15.csv     # 15-minute BTC data
├── ETHUSDT_1.csv      # 1-minute ETH data
├── ETHUSDT_5.csv      # 5-minute ETH data
└── ...               # Additional combinations
 
 
 
CSV Format 
csv
 
 
 
1
2
3
timestamp,datetime,open,high,low,close,volume
1757232000000,2025-09-07 11:30:00,0.007313,0.007313,0.007308,0.00731,4544.0
1757232060000,2025-09-07 11:31:00,0.00731,0.007315,0.00731,0.007312,3210.0
 
 
 
Field Descriptions 

     timestamp: Unix timestamp in milliseconds
     datetime: Human-readable format (YYYY-MM-DD HH:MM:SS)
     open/high/low/close: OHLC prices for the candle period
     volume: Trading volume during the candle period
     

5. Usage 
Installation 
bash
 
 
 
1
2
3
4
5
6
# Clone and setup
git clone <repository>
cd AIAssistedTradeBot
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
 
 
 
Running the System 
bash
 
 
 
1
2
# Starts GUI automatically (falls back to console if needed)
python main.py
 
 
 
GUI Interface 

     System Status: Real-time connection and processing status
     Configuration: Checkboxes for all major settings
     Controls: Start/Stop collection, Test Connection
     System Resources: Live CPU and Memory monitoring
     Error Tracking: Most recent errors displayed prominently
     Activity Log: Timestamped system events
     

Console Mode 

Automatic fallback with detailed logging: 

     Progress reporting for all operations
     Real-time status updates
     Memory usage monitoring
     Performance metrics
     

6. Current Status 
Phase 1 Completion ✅ 
Completed Components 

     Historical Data Fetcher: Multi-symbol concurrent fetching with rate limiting
     WebSocket Handler: Real-time data streaming with auto-reconnection
     Data Validator: Integrity checking and gap detection/filling
     CSV Manager: Efficient file operations with configurable retention
     GUI Interface: Professional monitoring and control interface
     System Integration: Hybrid historical + real-time data collection
     

Testing Requirements ✅ 

     Data accuracy verified against exchange API
     CSV file operations (read/write/update) tested
     Connection recovery and error handling validated
     Performance tested with multiple symbol sets (3, 50, 550+)
     

Quality Assurance ✅ 

     Modular, extensible architecture
     Comprehensive error handling
     Professional user interface
     Complete documentation
     

Performance Characteristics 

     Small Scale (3 symbols, 3 timeframes): 15-30 seconds, 50-100 MB
     Medium Scale (50 symbols, 3 timeframes): 2-5 minutes, 200-500 MB  
     Large Scale (550+ symbols, 3 timeframes): 10-20 minutes, 1-4 GB
     

7. Next Phase Integration 
Phase 2: Backtesting Engine 
Integration Points 
python
 
 
 
1
2
3
4
5
6
7
8
9
10
11
12
13
14
⌄
⌄
⌄
⌄
# Use existing data collection infrastructure
from hybrid_system import HybridTradingSystem

class BacktestingEngine:
    def __init__(self):
        self.data_system = HybridTradingSystem(config)
    
    def load_historical_data(self, symbols, timeframes):
        # Load data collected by Phase 1
        pass
    
    def run_backtest(self, strategy):
        # Use Phase 1 data for strategy testing
        pass
 
 
 
Required Interfaces 

     Data Access Layer: Standardized interface for accessing collected data
     Historical Data Loading: Efficient loading of CSV data into memory
     Real-time Simulation: Emulate real-time data flow for strategy testing
     

Phase 3: Strategy Development 
Data Interface Standardization 
python
 
 
 
1
2
3
4
5
6
7
8
9
10
11
⌄
⌄
⌄
⌄
class DataInterface:
    def __init__(self):
        self.data_system = HybridTradingSystem(config)
    
    def get_historical_data(self, symbol, timeframe, start, end):
        # Access Phase 1 collected data
        pass
    
    def get_real_time_stream(self, symbol, timeframe):
        # Integrate with Phase 1 WebSocket
        pass
 
 
 
Phase 4: Live Trading 
Integration Considerations 

     Data Continuity: Seamless transition from historical to live data
     Risk Management: Extend existing data validation to trading
     Performance Monitoring: Leverage existing system monitoring
     Error Handling: Extend error management to trading operations
     

8. Technical Specifications 
Dependencies 

     Python 3.8+
     aiohttp: Async HTTP client
     websockets: WebSocket client
     pybit: Bybit API client
     psutil: System monitoring
     

System Requirements 

     Memory: 4GB minimum, 8GB+ recommended for large datasets
     Storage: Several GB for data (depends on collection scope)
     Network: Stable internet connection for API access
     

Configuration Optimization 

     Conservative: BULK_BATCH_SIZE=10, BULK_REQUEST_DELAY_MS=100
     Balanced: BULK_BATCH_SIZE=20, BULK_REQUEST_DELAY_MS=50 (recommended)
     Aggressive: BULK_BATCH_SIZE=50, BULK_REQUEST_DELAY_MS=10
     

Error Handling 

     API Errors: Automatic retry with exponential backoff
     Connection Issues: Auto-reconnection with graceful degradation
     Data Errors: Validation and logging with continued processing
     System Errors: Resource monitoring and graceful degradation
     

9. Summary 

The AI Assisted TradeBot Phase 1 is a complete, production-ready data collection system that provides the foundation for advanced trading system development. It successfully combines historical data fetching with real-time data streaming, all managed through a professional user interface. 
Key Achievements 

     Complete data collection infrastructure for historical and real-time data
     Professional GUI with comprehensive monitoring capabilities
     Robust error handling and performance optimization
     Modular, extensible architecture ready for Phase 2 integration
     Comprehensive data validation and integrity management
     

Next Steps 

     Immediate Use: Start collecting data for strategy development
     Phase 2 Development: Design backtesting engine using collected data
     Strategy Development: Use the data interface for trading strategy creation
     Live Trading Integration: Plan for seamless transition to live operations
     

This system provides all necessary data collection and management capabilities required for building a comprehensive cryptocurrency trading bot. 