import argparse
import sys
from datetime import datetime
from config import DataCollectionConfig
from data_fetcher import FastDataFetcher

def main():
    """Main entry point for the data collection application"""
    config = DataCollectionConfig()
    
    parser = argparse.ArgumentParser(description='Fast Historical Data Collection for Trading Bot')
    parser.add_argument('--days', type=int, default=config.DAYS_TO_FETCH,
                       help=f'Number of days of historical data to fetch (default: {config.DAYS_TO_FETCH})')
    parser.add_argument('--symbols', nargs='+', default=config.SYMBOLS,
                       help=f'Symbols to fetch data for (default: {config.SYMBOLS})')
    parser.add_argument('--timeframes', nargs='+', default=config.TIMEFRAMES,
                       help=f'Timeframes to fetch data for (default: {config.TIMEFRAMES})')
    parser.add_argument('--limit-50', action='store_true', 
                       help='Limit data to 50 entries per symbol/timeframe')
    parser.add_argument('--full-data', action='store_true',
                       help='Fetch full historical data (no 50-entry limit)')
    parser.add_argument('--all-symbols', action='store_true',
                       help='Fetch data for all symbols from Bybit')
    parser.add_argument('--no-timing', action='store_true',
                       help='Hide detailed timing information')
    parser.add_argument('--no-stats', action='store_true',
                       help='Hide performance statistics')
    parser.add_argument('--check-integrity', action='store_true',
                       help='Check data integrity after fetching (overrides config)')
    parser.add_argument('--no-integrity', action='store_true',
                       help='Skip integrity check (overrides config)')
    parser.add_argument('--fix-duplicates', action='store_true',
                       help='Fix duplicate entries in all data files')
    parser.add_argument('--integrity-only', action='store_true',
                       help='Only run integrity check, no data fetching')
    parser.add_argument('--fill-gaps', action='store_true',
                       help='Fill gaps in data files (overrides config)')
    parser.add_argument('--no-gap-fill', action='store_true',
                       help='Skip gap filling (overrides config)')
    
    args = parser.parse_args()
    
    # Integrity checking mode (standalone)
    if args.integrity_only or args.fix_duplicates or args.fill_gaps:
        try:
            from data_integrity import DataIntegrityChecker
            integrity_checker = DataIntegrityChecker(config)
            
            if args.fix_duplicates:
                integrity_checker.fix_all_duplicates()
            
            if args.fill_gaps:
                integrity_checker.fill_all_gaps()
            
            if args.integrity_only:
                results = integrity_checker.check_all_files()
                
                print("\n" + "="*60)
                print("INTEGRITY CHECK RESULTS")
                print("="*60)
                print(f"Files checked: {results['files_checked']}")
                print(f"Files with issues: {results['files_with_issues']}")
                print(f"Total gaps: {results['total_gaps']}")
                print(f"Total duplicates: {results['total_duplicates']}")
                print(f"Total invalid candles: {results['total_invalid_candles']}")
                print("="*60)
            
            if args.integrity_only or args.fill_gaps or args.fix_duplicates:
                return
        except ImportError:
            print("Error: data_integrity.py not found. Please create the data_integrity.py file.")
            return
        except Exception as e:
            print(f"Error running integrity/gap filling: {e}")
            return
    
    # Update config with command line arguments
    if args.symbols != config.SYMBOLS:
        config.SYMBOLS = args.symbols
    
    if args.timeframes != config.TIMEFRAMES:
        config.TIMEFRAMES = args.timeframes
    
    # Handle data mode flags
    if args.limit_50:
        config.LIMIT_TO_50_ENTRIES = True
    elif args.full_data:
        config.LIMIT_TO_50_ENTRIES = False
    
    # Handle all symbols flag
    if args.all_symbols:
        config.FETCH_ALL_SYMBOLS = True
    
    # Handle display flags
    if args.no_timing:
        config.SHOW_DETAILED_TIMING = False
    if args.no_stats:
        config.SHOW_PERFORMANCE_STATS = False
    
    # Determine if we should run integrity check
    run_integrity = False
    
    # Priority: Command line arguments override config
    if args.check_integrity:
        run_integrity = True
    elif args.no_integrity:
        run_integrity = False
    else:
        # Use config setting if available
        run_integrity = getattr(config, 'RUN_INTEGRITY_CHECK', False)
    
    # Determine if we should run gap filling
    run_gap_filling = False
    
    # Priority: Command line arguments override config
    if args.fill_gaps:
        run_gap_filling = True
    elif args.no_gap_fill:
        run_gap_filling = False
    else:
        # Use config setting if available
        run_gap_filling = getattr(config, 'RUN_GAP_FILLING', False)
    
    # Create fetcher with updated config
    fetcher = FastDataFetcher(config)
    
    print(f"{'='*60}")
    print(f"FAST DATA COLLECTOR v2.0")
    print(f"{'='*60}")
    print(f"Configuration:")
    print(f"  Days: {args.days}")
    print(f"  Data mode: {'Limited to 50 entries' if config.LIMIT_TO_50_ENTRIES else 'Full historical data'}")
    print(f"  Symbols: {'All from Bybit' if config.FETCH_ALL_SYMBOLS else f'{len(config.SYMBOLS)} configured'}")
    print(f"  Timeframes: {config.TIMEFRAMES}")
    print(f"  Auto integrity check: {'Enabled' if run_integrity else 'Disabled'}")
    print(f"  Auto gap filling: {'Enabled' if run_gap_filling else 'Disabled'}")
    print(f"{'='*60}")
    
    # Fetch all data
    fetcher.fetch_all_data(args.days)
    
    # Run integrity check if enabled
    if run_integrity:
        try:
            print("\n" + "="*60)
            print("RUNNING AUTOMATIC INTEGRITY CHECK")
            print("="*60)
            
            from data_integrity import DataIntegrityChecker
            integrity_checker = DataIntegrityChecker(config)
            results = integrity_checker.check_all_files()
            
            print(f"\nIntegrity Check Results:")
            print(f"  Files checked: {results['files_checked']}")
            print(f"  Files with issues: {results['files_with_issues']}")
            print(f"  Total gaps: {results['total_gaps']}")
            print(f"  Total duplicates: {results['total_duplicates']}")
            print(f"  Total invalid candles: {results['total_invalid_candles']}")
            
            # Quick summary of issues found
            if results['files_with_issues'] > 0:
                print(f"\nIssues found in {results['files_with_issues']} files:")
                for filename, issues in results['issues'].items():
                    gap_count = len(issues['gaps'])
                    dup_count = issues['duplicate_count']
                    invalid_count = issues['invalid_candles']
                    
                    issues_list = []
                    if gap_count > 0:
                        issues_list.append(f"{gap_count} gaps")
                    if dup_count > 0:
                        issues_list.append(f"{dup_count} duplicates")
                    if invalid_count > 0:
                        issues_list.append(f"{invalid_count} invalid")
                    
                    print(f"  {filename}: {', '.join(issues_list)}")
                
                print(f"\nDetailed reports saved to: {integrity_checker.reports_dir}")
                print("To fix duplicates, run: python main.py --fix-duplicates")
            else:
                print("\n✓ All data files passed integrity check!")
                
        except ImportError:
            print("\nWarning: data_integrity.py not found. Skipping integrity check.")
            print("To enable integrity checking, create the data_integrity.py file.")
        except Exception as e:
            print(f"\nError running integrity check: {e}")
    
    # Run gap filling if enabled
    if run_gap_filling:
        try:
            print("\n" + "="*60)
            print("RUNNING AUTOMATIC GAP FILLING")
            print("="*60)
            
            from data_integrity import DataIntegrityChecker
            integrity_checker = DataIntegrityChecker(config)
            integrity_checker.fill_all_gaps()
            
            print("\n✓ Gap filling completed!")
                
        except ImportError:
            print("\nWarning: data_integrity.py not found. Skipping gap filling.")
            print("To enable gap filling, create the data_integrity.py file.")
        except Exception as e:
            print(f"\nError running gap filling: {e}")
    
    print("\nData collection completed!")

if __name__ == "__main__":
    main()


'''import argparse
import sys
from datetime import datetime
from config import DataCollectionConfig
from data_fetcher import FastDataFetcher

def main():
    """Main entry point for the data collection application"""
    config = DataCollectionConfig()
    
    parser = argparse.ArgumentParser(description='Fast Historical Data Collection for Trading Bot')
    parser.add_argument('--days', type=int, default=config.DAYS_TO_FETCH,
                       help=f'Number of days of historical data to fetch (default: {config.DAYS_TO_FETCH})')
    parser.add_argument('--symbols', nargs='+', default=config.SYMBOLS,
                       help=f'Symbols to fetch data for (default: {config.SYMBOLS})')
    parser.add_argument('--timeframes', nargs='+', default=config.TIMEFRAMES,
                       help=f'Timeframes to fetch data for (default: {config.TIMEFRAMES})')
    parser.add_argument('--limit-50', action='store_true', 
                       help='Limit data to 50 entries per symbol/timeframe')
    parser.add_argument('--full-data', action='store_true',
                       help='Fetch full historical data (no 50-entry limit)')
    parser.add_argument('--all-symbols', action='store_true',
                       help='Fetch data for all symbols from Bybit')
    parser.add_argument('--no-timing', action='store_true',
                       help='Hide detailed timing information')
    parser.add_argument('--no-stats', action='store_true',
                       help='Hide performance statistics')
    
    args = parser.parse_args()
    
    # Update config with command line arguments
    if args.symbols != config.SYMBOLS:
        config.SYMBOLS = args.symbols
    
    if args.timeframes != config.TIMEFRAMES:
        config.TIMEFRAMES = args.timeframes
    
    # NEW: Handle data mode flags
    if args.limit_50:
        config.LIMIT_TO_50_ENTRIES = True
    elif args.full_data:
        config.LIMIT_TO_50_ENTRIES = False
    
    # NEW: Handle all symbols flag
    if args.all_symbols:
        config.FETCH_ALL_SYMBOLS = True
    
    # NEW: Handle display flags
    if args.no_timing:
        config.SHOW_DETAILED_TIMING = False
    if args.no_stats:
        config.SHOW_PERFORMANCE_STATS = False
    
    # Create fetcher with updated config
    fetcher = FastDataFetcher(config)
    
    print(f"{'='*60}")
    print(f"FAST DATA COLLECTOR v2.0")
    print(f"{'='*60}")
    print(f"Configuration:")
    print(f"  Days: {args.days}")
    print(f"  Data mode: {'Limited to 50 entries' if config.LIMIT_TO_50_ENTRIES else 'Full historical data'}")
    print(f"  Symbols: {'All from Bybit' if config.FETCH_ALL_SYMBOLS else f'{len(config.SYMBOLS)} configured'}")
    print(f"  Timeframes: {config.TIMEFRAMES}")
    print(f"{'='*60}")
    
    # Fetch all data
    fetcher.fetch_all_data(args.days)
    
    print("Data collection completed!")

if __name__ == "__main__":
    main()'''