import argparse
import signal
import sys
from datetime import datetime, timedelta
from config import DataCollectionConfig
from csv_manager import CSVManager
from historical_fetcher import HistoricalDataFetcher
from websocket_handler import WebSocketHandler
from data_validator import DataValidator

class DataCollectionApp:
    def __init__(self):
        self.config = DataCollectionConfig()
        self.csv_manager = CSVManager(self.config.DATA_DIR, self.config.MAX_ENTRIES)
        self.historical_fetcher = HistoricalDataFetcher(self.config, self.csv_manager)
        self.ws_handler = WebSocketHandler(self.config, self.csv_manager)
        self.running = False
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down data collection...")
        self.stop()
        sys.exit(0)
    
    def fetch_historical_data(self, days_back: int = None):
        """Fetch historical data for all symbols and timeframes"""
        if days_back is None:
            days_back = self.config.DEFAULT_HISTORICAL_DAYS
            
        print(f"Fetching historical data for the last {days_back} days...")
        self.historical_fetcher.fetch_all_historical_data(days_back)
        print("Historical data fetching completed.")
    
    def start_real_time_collection(self):
        """Start real-time data collection via WebSocket"""
        print("Starting real-time data collection...")
        self.running = True
        self.ws_handler.start()
        
        # Keep the main thread alive
        try:
            while self.running:
                # Validate data periodically
                for symbol in self.config.SYMBOLS:
                    for timeframe in self.config.TIMEFRAMES:
                        data = self.csv_manager.read_data(symbol, timeframe)
                        if data and not DataValidator.validate_data_consistency(data):
                            print(f"Warning: Data inconsistency detected for {symbol} {timeframe}")
                
                # Sleep for a while
                import time
                time.sleep(60)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop all data collection"""
        self.running = False
        self.ws_handler.stop()
        print("Data collection stopped.")
    
    def run(self, args=None):
        """Main application entry point"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # If no arguments provided, use defaults from config
        if args is None:
            mode = self.config.DEFAULT_MODE
            days = self.config.DEFAULT_HISTORICAL_DAYS
        else:
            parser = argparse.ArgumentParser(description='Data Collection for Trading Bot')
            parser.add_argument('--historical', action='store_true', help='Fetch historical data only')
            parser.add_argument('--realtime', action='store_true', help='Start real-time data collection')
            parser.add_argument('--days', type=int, default=self.config.DEFAULT_HISTORICAL_DAYS, 
                              help=f'Number of days of historical data to fetch (default: {self.config.DEFAULT_HISTORICAL_DAYS})')
            
            args = parser.parse_args()
            
            # Determine mode based on arguments
            if args.historical and args.realtime:
                mode = 'both'
            elif args.historical:
                mode = 'historical'
            elif args.realtime:
                mode = 'realtime'
            else:
                mode = self.config.DEFAULT_MODE
            
            days = args.days
        
        # Execute based on mode
        if mode == 'historical':
            self.fetch_historical_data(days)
        elif mode == 'realtime':
            self.start_real_time_collection()
        elif mode == 'both':
            self.fetch_historical_data(days)
            self.start_real_time_collection()
        else:
            print(f"Invalid mode: {mode}")
            return 1
        
        return 0

if __name__ == "__main__":
    app = DataCollectionApp()
    sys.exit(app.run())