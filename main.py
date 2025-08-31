import argparse
import sys
from datetime import datetime
from config import DataCollectionConfig
from data_fetcher import FastDataFetcher

def main():
    """Main entry point for the data collection application"""
    config = DataCollectionConfig()
    fetcher = FastDataFetcher(config)
    
    parser = argparse.ArgumentParser(description='Fast Historical Data Collection for Trading Bot')
    parser.add_argument('--days', type=int, default=config.DAYS_TO_FETCH,
                       help=f'Number of days of historical data to fetch (default: {config.DAYS_TO_FETCH})')
    parser.add_argument('--symbols', nargs='+', default=config.SYMBOLS,
                       help=f'Symbols to fetch data for (default: {config.SYMBOLS})')
    parser.add_argument('--timeframes', nargs='+', default=config.TIMEFRAMES,
                       help=f'Timeframes to fetch data for (default: {config.TIMEFRAMES})')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    config.SYMBOLS = args.symbols
    config.TIMEFRAMES = args.timeframes
    
    print(f"Starting data collection at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Configuration: {config.DAYS_TO_FETCH} days, {len(config.SYMBOLS)} symbols, {len(config.TIMEFRAMES)} timeframes")
    
    # Fetch all data
    fetcher.fetch_all_data(args.days)
    
    print("Data collection completed!")

if __name__ == "__main__":
    main()