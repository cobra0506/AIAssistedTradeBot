"""
Backtester Engine Component - Phase 1.1
Core backtesting logic that processes data and executes strategies
Integrates with DataFeeder for data access and StrategyBase for signal generation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from simple_strategy.backtester.risk_manager import RiskManager
from simple_strategy.backtester.performance_tracker import PerformanceTracker
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
# Fix import paths - shared is a sibling directory, not a subdirectory
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.data_feeder import DataFeeder
from shared.strategy_base import StrategyBase

# Configure logging to reduce debug output
logging.basicConfig(
    level=logging.WARNING,  # Change from INFO to WARNING to reduce output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Specifically set debug level for backtester to WARNING
logging.getLogger('simple_strategy.backtester.backtester_engine').setLevel(logging.WARNING)
logging.getLogger('simple_strategy.strategies.strategy_builder').setLevel(logging.WARNING)

# Create logger instance for this module
logger = logging.getLogger(__name__)

class BacktesterEngine:
    """
    Core backtesting engine that processes historical data and executes strategies
    """
    def __init__(self, data_feeder: DataFeeder, strategy: StrategyBase,
                 risk_manager: Optional[RiskManager] = None, config: Dict[str, Any] = None):
        """
        Initialize backtester engine with risk management integration
        Args:
            data_feeder: DataFeeder instance for data access
            strategy: StrategyBase instance for signal generation
            risk_manager: RiskManager instance for risk management (optional)
            config: Backtester configuration
        """
        self.data_feeder = data_feeder
        self.strategy = strategy
        self.risk_manager = risk_manager or RiskManager()  # Use default if not provided
        self.config = config or {}
        
        # Backtester state
        self.is_running = False
        self.current_timestamp = None
        self.processed_data = {}
        self.results = {}
        
        # Performance tracking
        self.start_time = None
        self.end_time = None
        self.processing_stats = {
            'total_rows_processed': 0,
            'total_signals_generated': 0,
            'total_trades_executed': 0,
            'processing_speed_rows_per_sec': 0
        }
        
        # Configuration
        self.processing_mode = self.config.get('processing_mode', 'sequential')  # 'sequential' or 'parallel'
        self.batch_size = self.config.get('batch_size', 1000)
        self.memory_limit_percent = self.config.get('memory_limit_percent', 70)
        self.enable_parallel_processing = self.config.get('enable_parallel_processing', False)
        
        # Initialize performance tracker
        self.performance_tracker = PerformanceTracker(initial_balance=10000)

        # Position tracking
        self.positions = {}  # Track open positions by symbol

        logger.info(f"BacktesterEngine initialized with strategy: {strategy.name}")
        logger.info(f"Risk management {'enabled'if self.risk_manager else'disabled'}")

    def run_backtest(self, symbols, timeframes, start_date, end_date, config=None, strategy=None, data=None, initial_balance=None):
        """
        Run backtest with optimized parameters loading
        """
        import time
        
        # Add timing at the very beginning
        start_time = time.time()
        print(f"🔧 DEBUG: Backtest started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load optimized parameters if available
        try:
            from simple_strategy.trading.parameter_manager import ParameterManager
            pm = ParameterManager()
            strategy_name = self.strategy.name if hasattr(self.strategy, 'name') else self.strategy.__class__.__name__
            optimized_params = pm.get_parameters(strategy_name)
            
            if optimized_params and 'last_optimized' in optimized_params:
                # Remove the last_optimized field as it's not a strategy parameter
                strategy_params = {k: v for k, v in optimized_params.items() if k != 'last_optimized'}
                
                # Update strategy parameters by directly setting attributes
                for param, value in strategy_params.items():
                    if hasattr(self.strategy, param):
                        setattr(self.strategy, param, value)
                    elif hasattr(self.strategy, 'params'):
                        self.strategy.params[param] = value
                
                print(f"✅ Using optimized parameters for {strategy_name} (optimized on {optimized_params['last_optimized']})")
        except Exception as e:
            print(f"⚠️ Could not load optimized parameters: {e}")
        
        try:
            # Get initial balance from parameter, config, or use default
            initial_balance = initial_balance or (config['initial_balance'] if config and 'initial_balance' in config else 10000.0)
            
            # Use provided strategy or fall back to self.strategy
            if strategy is None:
                strategy = self.strategy
                # Add timing right after strategy is determined
                print(f"🔧 DEBUG: Using strategy: {strategy.__class__.__name__}")

                # Debug strategy parameters
                print(f"🔧 DEBUG: Strategy attributes:")
                for attr in dir(strategy):
                    if not attr.startswith('_') and not callable(getattr(strategy, attr)):
                        try:
                            value = getattr(strategy, attr)
                            if not isinstance(value, (type, type(lambda: None), type(print))):
                                print(f"  - {attr}: {value}")
                        except:
                            pass

                # Check if strategy has params attribute
                if hasattr(strategy, 'params'):
                    print(f"🔧 DEBUG: Strategy params: {strategy.params}")
                else:
                    print(f"🔧 DEBUG: Strategy has no params attribute")
                print(f"🔧 DEBUG: Using self.strategy: {strategy.__class__.__name__}")
            else:
                print(f"🔧 DEBUG: Using provided strategy: {strategy.__class__.__name__}")
            
            # Add timing before data loading
            data_load_start = time.time()
            
            # Use provided data or load it using data_feeder
            if data is None:
                data = self.data_feeder.get_data_for_symbols(
                    symbols or strategy.symbols, 
                    timeframes or strategy.timeframes,
                    start_date or datetime.now() - timedelta(days=30),
                    end_date or datetime.now()
                )
            
            # Add timing after data loading
            data_load_time = time.time() - data_load_start
            print(f"🔧 DEBUG: Data loading took {data_load_time:.2f} seconds")
            
            # Print data info
            total_data_points = 0
            for symbol in data:
                for timeframe in data[symbol]:
                    df = data[symbol][timeframe]
                    total_data_points += len(df)
            print(f"🔧 DEBUG: Total data points to process: {total_data_points}")
            
            # Add timing before processing
            processing_start = time.time()
            
            # Initialize variables
            self.trades = []
            self.balance = initial_balance
            self.initial_balance = initial_balance

            # Initialize performance tracker with initial balance
            self.performance_tracker = PerformanceTracker(initial_balance=initial_balance)
            
            # Calculate total processing steps for progress tracking
            total_steps = 0
            for symbol in data:
                for timeframe in data[symbol]:
                    df = data[symbol][timeframe]
                    total_steps += len(df)
            
            processed_steps = 0
            last_progress_update = 0
            
            logger.info(f"🔧 Starting backtest with {total_steps} total data points")
            
            # Add timing before the main processing loop
            loop_start = time.time()

            # Calculate total rows for progress tracking
            total_rows = sum(len(data[symbol][timeframe]) for symbol in data for timeframe in data[symbol])
            processed_rows = 0
            last_progress_update = 0
            print(f"🔧 DEBUG: Total rows to process: {total_rows}")

            # Process each symbol and timeframe
            for symbol in data:
                for timeframe in data[symbol]:
                    df = data[symbol][timeframe].copy()
                    
                    logger.info(f"🔧 Processing {symbol} {timeframe}: {len(df)} rows")
                    
                    # Process each row
                    for i, (timestamp, row) in enumerate(df.iterrows()):

                        # Update progress
                        processed_rows += 1
                        progress_percent = (processed_rows / total_rows) * 100

                        # Update progress every 5% or for the last update
                        if progress_percent - last_progress_update >= 5 or progress_percent == 100:
                            print(f"🔧 DEBUG: Overall progress: {progress_percent:.1f}% ({processed_rows}/{total_rows} rows)")
                            last_progress_update = progress_percent
                            
                        # Create the proper data structure for signal generation
                        current_data = {symbol: {timeframe: df.loc[:timestamp]}}
                        
                        # Add timing for signal generation
                        signal_start = time.time()
                        
                        # Cache for signal generation to avoid recalculating
                        signal_cache_key = f"{symbol}_{timeframe}_{timestamp}"
                        if not hasattr(self, '_signal_cache'):
                            self._signal_cache = {}

                        if signal_cache_key in self._signal_cache:
                            signals = self._signal_cache[signal_cache_key]
                        else:
                            # Add timing for signal generation
                            signal_start = time.time()
                            
                            # Generate signals
                            signals = strategy.generate_signals(current_data)
                            
                            # Cache the result
                            self._signal_cache[signal_cache_key] = signals
                            
                            # Add timing after signal generation
                            signal_time = time.time() - signal_start
                            if signal_time > 0.01:  # Only log if it takes more than 10ms
                                print(f"🔧 DEBUG: Signal generation took {signal_time:.4f} seconds for {symbol} {timeframe}")

                        # Generate signals
                        signals = strategy.generate_signals(current_data)
                        
                        # Add timing after signal generation
                        signal_time = time.time() - signal_start
                        if signal_time > 0.01:  # Only log if it takes more than 10ms
                            print(f"🔧 DEBUG: Signal generation took {signal_time:.4f} seconds for {symbol} {timeframe}")

                        # Execute trades based on signals
                        signal = signals[symbol][timeframe]
                        if signal in ['BUY', 'SELL']:
                            # Create proper data structure for trade execution
                            trade_data = {symbol: {timeframe: df.loc[:timestamp]}}
                            trade_result = self._execute_trade(symbol, signal, timestamp, trade_data)
                            
                            if trade_result.get('executed', False):
                                current_price = row['close']
                                quantity = trade_result.get('quantity', 0)
                                
                                if signal == 'BUY':
                                    # For BUY signals, open a new position or add to existing
                                    if symbol not in self.positions:
                                        # Open new position
                                        self.positions[symbol] = {
                                            'entry_price': current_price,
                                            'quantity': quantity,
                                            'entry_timestamp': timestamp,
                                            'is_short': False  # Mark this as a long position
                                        }
                                        logger.info(f"DEBUG: Opened BUY position for {symbol} at {current_price}, qty={quantity}")
                                    else:
                                        # Check if this is a short position that needs to be closed
                                        if self.positions[symbol].get('is_short', False):
                                            # Close the short position
                                            position = self.positions[symbol]
                                            entry_price = position['entry_price']
                                            entry_timestamp = position['entry_timestamp']
                                            short_quantity = position['quantity']
                                            
                                            # Calculate PnL for short position (we profit when price goes down)
                                            pnl = (entry_price - current_price) * short_quantity
                                            
                                            # Record the completed trade
                                            logger.info(f"DEBUG: Closing SHORT position with BUY: entry={entry_price}, exit={current_price}, qty={short_quantity}, pnl={pnl}")
                                            
                                            self.performance_tracker.record_trade({
                                                'symbol': symbol,
                                                'direction': 'BUY',  # We're using a BUY to close a short
                                                'entry_price': entry_price,
                                                'exit_price': current_price,
                                                'size': short_quantity,
                                                'entry_timestamp': entry_timestamp,
                                                'exit_timestamp': timestamp,
                                                'pnl': pnl
                                            })
                                            
                                            # Remove the short position
                                            del self.positions[symbol]
                                            
                                            # Open a new long position
                                            self.positions[symbol] = {
                                                'entry_price': current_price,
                                                'quantity': quantity,
                                                'entry_timestamp': timestamp,
                                                'is_short': False
                                            }
                                            logger.info(f"DEBUG: Opened BUY position for {symbol} at {current_price}, qty={quantity}")
                                        else:
                                            # Add to existing long position
                                            old_qty = self.positions[symbol]['quantity']
                                            old_price = self.positions[symbol]['entry_price']
                                            new_qty = old_qty + quantity
                                            # Calculate weighted average entry price
                                            new_entry_price = ((old_price * old_qty) + (current_price * quantity)) / new_qty
                                            self.positions[symbol]['entry_price'] = new_entry_price
                                            self.positions[symbol]['quantity'] = new_qty
                                            logger.info(f"DEBUG: Added to BUY position for {symbol}: avg_price={new_entry_price}, total_qty={new_qty}")
                                
                                elif signal == 'SELL':
                                    # For SELL signals, close the position and calculate PnL
                                    if symbol in self.positions:
                                        position = self.positions[symbol]
                                        entry_price = position['entry_price']
                                        entry_timestamp = position['entry_timestamp']
                                        quantity = position['quantity']  # Sell the entire position
                                        
                                        # Calculate PnL
                                        pnl = (current_price - entry_price) * quantity
                                        
                                        # Record the completed trade
                                        logger.info(f"DEBUG: Recording SELL trade: entry={entry_price}, exit={current_price}, qty={quantity}, pnl={pnl}")
                                        
                                        success = self.performance_tracker.record_trade({
                                            'symbol': symbol,
                                            'direction': 'SELL',
                                            'entry_price': entry_price,
                                            'exit_price': current_price,
                                            'size': quantity,
                                            'entry_timestamp': entry_timestamp,
                                            'exit_timestamp': timestamp,
                                            'pnl': pnl
                                        })
                                        
                                        logger.info(f"DEBUG: Trade recording success: {success}")
                                        
                                        # Remove the position
                                        del self.positions[symbol]
                                        
                                        # Open a new short position for this SELL signal
                                        self.positions[symbol] = {
                                            'entry_price': current_price,
                                            'quantity': quantity,  # Use the same quantity we just sold
                                            'entry_timestamp': timestamp,
                                            'is_short': True  # Mark this as a short position
                                        }
                                        logger.info(f"DEBUG: Opened SHORT position for {symbol} at {current_price}, qty={quantity}")
                                    else:
                                        # No open position, open a new short position
                                        self.positions[symbol] = {
                                            'entry_price': current_price,
                                            'quantity': quantity,
                                            'entry_timestamp': timestamp,
                                            'is_short': True  # Mark this as a short position
                                        }
                                        logger.info(f"DEBUG: Opened SHORT position for {symbol} at {current_price}, qty={quantity}")
                        
                        # Update progress
                        processed_steps += 1
                        progress_percent = (processed_steps / total_steps) * 100
                        
                        # Update progress every 5% or for the last update
                        if progress_percent - last_progress_update >= 5 or progress_percent == 100:
                            logger.info(f"🔧 Backtest progress: 100.0%")
                            logger.info(f"🔧 Completed {symbol}{timeframe}")

            # Add timing after the main processing loop
            loop_time = time.time() - loop_start
            print(f"🔧 DEBUG: Main processing loop took {loop_time:.2f} seconds")
            
            # Add timing before closing positions
            close_positions_start = time.time()
            
            # Close any remaining positions at the end of backtest
            for symbol, position in self.positions.items():
                # Get the last timestamp and price for this symbol
                last_symbol_data = None
                for timeframe in data[symbol]:
                    if last_symbol_data is None or data[symbol][timeframe].index[-1] > last_symbol_data.index[-1]:
                        last_symbol_data = data[symbol][timeframe]
                
                if last_symbol_data is not None:
                    current_price = last_symbol_data.iloc[-1]['close']
                    entry_price = position['entry_price']
                    entry_timestamp = position['entry_timestamp']
                    quantity = position['quantity']
                    is_short = position.get('is_short', False)
                    
                    # Calculate final PnL based on position type
                    if is_short:
                        # For short positions, we profit when price goes down
                        pnl = (entry_price - current_price) * quantity
                        direction = 'BUY'  # We use a BUY to close a short position
                    else:
                        # For long positions, we profit when price goes up
                        pnl = (current_price - entry_price) * quantity
                        direction = 'SELL'  # We use a SELL to close a long position
                    
                    # Record the completed trade
                    logger.info(f"DEBUG: Closing final {'SHORT' if is_short else 'LONG'} position for {symbol}: entry={entry_price}, exit={current_price}, qty={quantity}, pnl={pnl}")
                    
                    self.performance_tracker.record_trade({
                        'symbol': symbol,
                        'direction': direction,
                        'entry_price': entry_price,
                        'exit_price': current_price,
                        'size': quantity,
                        'entry_timestamp': entry_timestamp,
                        'exit_timestamp': last_symbol_data.index[-1],
                        'pnl': pnl
                    })

            # Add timing after closing positions
            close_positions_time = time.time() - close_positions_start
            print(f"🔧 DEBUG: Closing positions took {close_positions_time:.2f} seconds")
            
            # Add timing before calculating metrics
            metrics_start = time.time()
            
            # Calculate and display performance metrics
            metrics = self._calculate_performance_metrics()
            self._display_results(metrics)

            # Add timing after calculating metrics
            metrics_time = time.time() - metrics_start
            print(f"🔧 DEBUG: Calculating metrics took {metrics_time:.2f} seconds")
            
            # Add total timing
            total_time = time.time() - start_time
            print(f"🔧 DEBUG: Total backtest time: {total_time:.2f} seconds")

            # Return metrics for GUI
            return {
                'win_rate': metrics['win_rate_pct'],
                'sharpe_ratio': metrics['sharpe_ratio'],
                'max_drawdown': metrics['max_drawdown_pct'],
                'total_return': metrics['total_return_pct'],
                'total_trades': metrics['total_trades']
            }

        except Exception as e:
            logger.error(f"Error in backtest: {e}")
            return {
                'win_rate': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_return': 0.0,
                'total_trades': 0
            }
    
    def _validate_data(self, data: Dict[str, Dict[str, pd.DataFrame]], 
                      symbols: List[str], timeframes: List[str]) -> bool:
        """
        Validate loaded data structure and content
        
        Args:
            data: Data dictionary from DataFeeder
            symbols: Expected symbols
            timeframes: Expected timeframes
            
        Returns:
            True if data is valid, False otherwise
        """
        logger.info("Validating data structure...")
        
        # Check all symbols are present
        for symbol in symbols:
            if symbol not in data:
                logger.error(f"Missing data for symbol: {symbol}")
                return False
            
            # Check all timeframes are present for each symbol
            for timeframe in timeframes:
                if timeframe not in data[symbol]:
                    logger.error(f"Missing data for {symbol} timeframe: {timeframe}")
                    return False
                
                # Check DataFrame is not empty
                df = data[symbol][timeframe]
                if df.empty:
                    logger.error(f"Empty DataFrame for {symbol} {timeframe}")
                    return False
                
                # Check required columns
                required_columns = ['open', 'high', 'low', 'close', 'volume']
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    logger.error(f"Missing columns for {symbol} {timeframe}: {missing_columns}")
                    return False
        
        logger.info("Data validation passed")
        return True
    
    def _process_data_chronologically(self, data: Dict[str, Dict[str, pd.DataFrame]],
                                symbols: List[str], timeframes: List[str]) -> Dict[str, Any]:
        """Process data chronologically and execute strategy signals"""
        try:
            # Get all unique timestamps across all symbols and timeframes
            all_timestamps = set()
            for symbol in symbols:
                for timeframe in timeframes:
                    if symbol in data and timeframe in data[symbol]:
                        all_timestamps.update(data[symbol][timeframe].index)
            
            # Sort timestamps
            sorted_timestamps = sorted(all_timestamps)
            
            # Initialize results tracking
            results = {
                'equity_curve': [],
                'trades': [],
                'signals': [],
                'timestamps': [],
                'portfolio_values': []
            }
            
            # Track first few signals for debugging
            signal_count = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            
            # Process each timestamp
            for i, timestamp in enumerate(sorted_timestamps):
                if not self.is_running:
                    break
                
                # Get data for current timestamp across all symbols and timeframes
                current_data = self._get_data_for_timestamp(data, symbols, timeframes, timestamp)
                
                # Generate signals using strategy
                signals = self.strategy.generate_signals(current_data)
                
                # Count signals for debugging
                for symbol, timeframe_signals in signals.items():
                    for timeframe, signal in timeframe_signals.items():
                        signal_count[signal] += 1
                
                # Process signals and execute trades
                trade_results = self._process_signals(signals, current_data, timestamp)
                
                # Update results
                self._update_results(results, signals, trade_results, timestamp)
                
                # Update processing stats
                self.processing_stats['total_rows_processed'] += len(symbols) * len(timeframes)
                self.processing_stats['total_signals_generated'] += len([s for s in signals.values() if s != 'HOLD'])
                
                # Log progress every 1000 timestamps
                if i % 1000 == 0:
                    progress = (i / len(sorted_timestamps)) * 100
                    print(f"🔧 Processing progress: {progress:.1f}%")
            
            # Print signal summary for debugging
            print(f"🔧 Signal summary: BUY={signal_count['BUY']}, SELL={signal_count['SELL']}, HOLD={signal_count['HOLD']}")
            print(f"🔧 Processing complete. Generated {len(results['trades'])} trades")
            
            return results
        except Exception as e:
            print(f"🔧 Error in _process_data_chronologically: {e}")
            import traceback
            print(f"🔧 Full traceback: {traceback.format_exc()}")
            return {'error': str(e)}
        
    def _can_execute_trade(self, symbol: str, signal: str, timestamp: datetime, current_data: Dict[str, Dict[str, pd.DataFrame]] = None) -> bool:
        """
        Check if a trade can be executed based on current positions and risk rules
        Args:
            symbol: Trading symbol
            signal: Trade signal ('BUY' or 'SELL')
            timestamp: Current timestamp
            current_data: Current market data (optional)
        Returns:
            True if trade can be executed, False otherwise
        """
        try:
            # Check if we already have a position for this symbol
            has_position = symbol in self.strategy.positions and self.strategy.positions[symbol].get('size', 0) > 0
            
            # For BUY signals, check if we already have a position
            if signal == 'BUY' and has_position:
                logger.info(f"⚠️ Already have position for {symbol}, skipping BUY")
                return False
            
            # For SELL signals, check if we have a position to sell
            if signal == 'SELL' and not has_position:
                logger.info(f"⚠️ No position to sell for {symbol}, skipping SELL")
                return False
            
            # Get current price for risk management
            current_price = 0.0
            if current_data:
                current_price = self._get_current_price(symbol, current_data)
            else:
                logger.warning(f"⚠️ No current data provided for {symbol}, using default price")
                # Use a reasonable default price based on the strategy balance
                current_price = 20000.0  # Default BTC price
            
            # Check risk management rules
            if self.risk_manager:
                account_state = {
                    'balance': self.strategy.balance,
                    'positions': self.strategy.positions
                }
                
                trade_signal = {
                    'symbol': symbol,
                    'signal_type': signal,
                    'price': current_price,
                    'timestamp': timestamp
                }
                
                validation_result = self.risk_manager.validate_trade_signal(trade_signal, account_state)
                if not validation_result['valid']:
                    logger.info(f"⚠️ Risk management blocked {signal} trade for {symbol}: {validation_result.get('reason', 'Unknown reason')}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking if trade can be executed for {symbol}: {e}")
            return False
    
    def _get_data_for_timestamp(self, data: Dict[str, Dict[str, pd.DataFrame]],
                           symbols: List[str], timeframes: List[str],
                           timestamp: datetime) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Get data for a specific timestamp across all symbols and timeframes
        Args:
            data: Full data dictionary
            symbols: Trading symbols
            timeframes: Timeframes
            timestamp: Target timestamp
        Returns:
            Data dictionary for the specific timestamp with historical data
        """
        timestamp_data = {}
        
        for symbol in symbols:
            timestamp_data[symbol] = {}
            
            for timeframe in timeframes:
                df = data[symbol][timeframe]
                
                # Get all data up to and including the target timestamp
                # This is crucial for indicators that need historical data
                mask = df.index <= timestamp
                
                if mask.any():
                    # Get all historical data up to this timestamp
                    historical_data = df[mask].copy()
                    timestamp_data[symbol][timeframe] = historical_data
                else:
                    # No data before this timestamp
                    timestamp_data[symbol][timeframe] = df.iloc[0:0]  # Empty DataFrame
        
        return timestamp_data
    
    def _process_signals(self, signals: Dict[str, Dict[str, str]], current_data: Dict[str, Dict[str, pd.DataFrame]], timestamp: datetime) -> List[Dict[str, Any]]:
        """Process signals and execute trades"""
        trade_results = []
        
        try:
            for symbol, timeframe_signals in signals.items():
                for timeframe, signal in timeframe_signals.items():
                    if signal in ['BUY', 'SELL']:
                        # Check if we can execute this trade (pass current_data)
                        if self._can_execute_trade(symbol, signal, timestamp, current_data):
                            # Execute the trade
                            trade_result = self._execute_trade(symbol, signal, timestamp, current_data)
                            trade_results.append(trade_result)
                        else:
                            logger.info(f"⚠️ Cannot execute {signal} trade for {symbol} at {timestamp}")
            
            return trade_results
            
        except Exception as e:
            logger.error(f"❌ Error processing signals: {e}")
            return []
    
    def _get_current_price(self, symbol: str, current_data: Dict[str, Dict[str, pd.DataFrame]]) -> float:
        """Get current price for a symbol from the current data"""
        try:
            # Check if current_data is the expected structure
            if not isinstance(current_data, dict) or symbol not in current_data:
                logger.warning(f"⚠️ Invalid data structure for {symbol}")
                return 50000.0  # Return a reasonable default price
            
            # Get the first timeframe data for this symbol
            if not current_data[symbol]:
                logger.warning(f"⚠️ No timeframe data for {symbol}")
                return 50000.0
            
            # Get the first timeframe DataFrame
            timeframe_data = list(current_data[symbol].values())[0]
            
            if timeframe_data.empty:
                logger.warning(f"⚠️ Empty DataFrame for {symbol}")
                return 50000.0
            
            # Get the last close price
            current_price = timeframe_data['close'].iloc[-1]
            
            # Ensure it's a valid price
            if pd.isna(current_price) or current_price <= 0:
                logger.warning(f"⚠️ Invalid price {current_price} for {symbol}")
                return 50000.0
            
            return float(current_price)
            
        except Exception as e:
            logger.error(f"❌ Error getting current price for {symbol}: {e}")
            # Return a reasonable default instead of 0
            return 50000.0
    
    def _execute_trade(self, symbol: str, signal: str, timestamp: datetime, current_data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
        """Execute a trade based on signal"""
        try:
            # Get current price using the proper data structure
            current_price = self._get_current_price(symbol, current_data)
            
            # Safety check for zero price
            if current_price <= 0:
                logger.warning(f"⚠️ Invalid price {current_price} for {symbol}, skipping trade")
                return {'executed': False, 'reason': 'invalid_price'}
            
            # Calculate position size - pass the current price
            position_size = self.strategy.calculate_position_size(symbol, current_price=current_price)
            
            # Log the trade execution attempt
            logger.info(f"📊 Executing {signal} trade for {symbol} at {current_price}")
            
            # Check if we have enough balance
            trade_cost = position_size * current_price
            available_balance = self.strategy.balance
            
            if trade_cost > available_balance:
                logger.info(f"⚠️ Insufficient balance for {symbol} {signal}: needed=${trade_cost:.2f}, available=${available_balance:.2f}")
                return {'executed': False, 'reason': 'insufficient_balance'}
            
            # Execute the trade
            trade_result = {
                'symbol': symbol,
                'signal': signal,
                'timestamp': timestamp,
                'price': current_price,
                'quantity': position_size,
                'cost': trade_cost,
                'executed': True
            }
            
            # Update strategy balance
            if signal == 'BUY':
                self.strategy.balance -= trade_cost
                # Track the position for later PnL calculation
                if symbol not in self.strategy.positions:
                    self.strategy.positions[symbol] = {}
                self.strategy.positions[symbol]['entry_price'] = current_price
                self.strategy.positions[symbol]['quantity'] = position_size
            elif signal == 'SELL':
                self.strategy.balance += trade_cost
                # Remove the position and calculate PnL
                if symbol in self.strategy.positions:
                    entry_price = self.strategy.positions[symbol].get('entry_price', current_price)
                    quantity = self.strategy.positions[symbol].get('quantity', position_size)
                    # Calculate PnL
                    pnl = (current_price - entry_price) * quantity
                    trade_result['pnl'] = pnl
                    del self.strategy.positions[symbol]
            
            logger.info(f"✅ Executed {signal} trade: {position_size:.6f} {symbol} at ${current_price:.2f}")
            
            return trade_result
            
        except Exception as e:
            logger.error(f"❌ Error executing trade for {symbol}: {e}")
            return {'executed': False, 'reason': str(e)}
    
    def _update_results(self, results: Dict[str, Any], signals: Dict[str, Dict[str, str]], trade_results: List[Dict[str, Any]], timestamp: datetime):
        """Update results with new signals and trades"""
        try:
            # Update signals
            results['signals'].append({
                'timestamp': timestamp,
                'signals': signals
            })
            
            # Update trades
            results['trades'].extend(trade_results)
            
            # Update timestamps
            results['timestamps'].append(timestamp)
            
            # Calculate current portfolio value
            current_value = self.strategy.balance
            
            # Add value of open positions
            for symbol, position in self.strategy.positions.items():
                if position.get('size', 0) > 0:
                    # Get current price (this is a simplified approach)
                    current_price = position.get('current_price', position.get('entry_price', 0))
                    position_value = position['size'] * current_price
                    current_value += position_value
            
            # Update portfolio values
            results['portfolio_values'].append({
                'timestamp': timestamp,
                'value': current_value
            })
            
            # Update equity curve
            results['equity_curve'].append({
                'timestamp': timestamp,
                'value': current_value
            })
            
        except Exception as e:
            logger.error(f"❌ Error updating results: {e}")
    
    def _calculate_final_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate final backtest results from intermediate results
        Args:
            results: Intermediate results from _process_data_chronologically
        Returns:
            Final results dictionary
        """
        try:
            logger.debug("🔧 DEBUG: _calculate_final_results called")
            
            # Check if results contains an error
            if 'error' in results:
                logger.error(f"❌ Error in backtest processing: {results['error']}")
                return {'error': results['error']}
            
            # Calculate performance metrics
            final_results = {
                'equity_curve': results.get('equity_curve', []),
                'trades': results.get('trades', []),
                'signals': results.get('signals', []),
                'timestamps': results.get('timestamps', []),
                'portfolio_values': results.get('portfolio_values', []),
                'performance_metrics': {}
            }
            
            # Calculate basic metrics
            if final_results['trades']:
                total_trades = len(final_results['trades'])
                winning_trades = len([t for t in final_results['trades'] if t.get('pnl', 0) > 0])
                losing_trades = total_trades - winning_trades
                
                final_results['performance_metrics']['total_trades'] = total_trades
                final_results['performance_metrics']['winning_trades'] = winning_trades
                final_results['performance_metrics']['losing_trades'] = losing_trades
                
                if total_trades > 0:
                    win_rate = winning_trades / total_trades
                    final_results['performance_metrics']['win_rate'] = win_rate
            
            # Calculate equity-based metrics
            if final_results['equity_curve']:
                # Handle the case where equity curve contains dictionaries
                if isinstance(final_results['equity_curve'][0], dict):
                    # Extract values from dictionaries
                    initial_equity = final_results['equity_curve'][0].get('value', 10000) if final_results['equity_curve'] else 10000
                    final_equity = final_results['equity_curve'][-1].get('value', 10000) if final_results['equity_curve'] else initial_equity
                else:
                    # Direct numeric values
                    initial_equity = final_results['equity_curve'][0] if final_results['equity_curve'] else 10000
                    final_equity = final_results['equity_curve'][-1] if final_results['equity_curve'] else initial_equity
                
                total_return = (final_equity - initial_equity) / initial_equity if initial_equity != 0 else 0
                final_results['performance_metrics']['total_return'] = total_return
                final_results['performance_metrics']['initial_equity'] = initial_equity
                final_results['performance_metrics']['final_equity'] = final_equity
            
            # Add processing stats
            final_results['processing_stats'] = self.processing_stats
            
            # Add execution time
            if self.start_time and self.end_time:
                execution_time = self.end_time - self.start_time
                final_results['execution_time'] = execution_time
            
            logger.debug("✅ Final results calculated successfully")
            return final_results
        
        except Exception as e:
            logger.error(f"❌ Error calculating final results: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            return {'error': str(e)}
    
    def stop_backtest(self):
        """Stop the currently running backtest"""
        logger.info("Stopping backtest...")
        self.is_running = False

    def calculate_performance_metrics(self, trades, initial_balance, final_balance):
        """
        Calculate comprehensive performance metrics
        """
        if not trades:
            return {
                'win_rate': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'total_return': 0.0
            }
        
        # Calculate win rate
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        
        # Calculate total return
        total_return = ((final_balance - initial_balance) / initial_balance) * 100
        
        # Calculate Sharpe ratio (simplified)
        if len(trades) > 1:
            pnl_list = [t.get('pnl', 0) for t in trades]
            avg_return = sum(pnl_list) / len(pnl_list)
            std_return = (sum((x - avg_return) ** 2 for x in pnl_list) / len(pnl_list)) ** 0.5
            sharpe_ratio = (avg_return / std_return) * (252 ** 0.5) if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Calculate max drawdown (simplified)
        max_drawdown = 0.0
        peak_balance = initial_balance
        
        for trade in trades:
            current_balance = trade.get('balance_after', initial_balance)
            if current_balance > peak_balance:
                peak_balance = current_balance
            
            drawdown = ((peak_balance - current_balance) / peak_balance) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'win_rate': win_rate * 100,  # Convert to percentage
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_return': total_return
        }

    def display_results(self, performance_metrics):
        """
        Display backtest results in a formatted way
        """
        print("\n" + "="*50)
        print("📊 BACKTEST RESULTS")
        print("="*50)
        print(f"💰 Total Return: {performance_metrics['total_return']:.2f}%")
        print(f"🎯 Win Rate: {performance_metrics['win_rate']:.2f}%")
        print(f"📈 Sharpe Ratio: {performance_metrics['sharpe_ratio']:.2f}")
        print(f"📉 Max Drawdown: {performance_metrics['max_drawdown']:.2f}%")
        print(f"🔄 Total Trades: {len(self.trades)}")
        print("="*50)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current backtest statusrun_backtest
        
        Returns:
            Status dictionary
        """
        return {
            'is_running': self.is_running,
            'current_timestamp': self.current_timestamp,
            'processing_stats': self.processing_stats,
            'strategy_state': self.strategy.get_strategy_state() if hasattr(self.strategy, 'get_strategy_state') else None
        }
    
    def _calculate_performance_metrics(self):
        """Calculate performance metrics from trades"""
        logger.info(f"DEBUG: Calculating metrics with {len(self.performance_tracker.trades)} trades")
        
        if not self.performance_tracker.trades:
            logger.info("DEBUG: No trades found in performance tracker")
            return {
                'total_return_pct': 0.0,
                'win_rate_pct': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown_pct': 0.0,
                'total_trades': 0
            }
        
        trades = self.performance_tracker.trades
        total_trades = len(trades)
        logger.info(f"DEBUG: Processing {total_trades} trades")
        
        # Debug: Print first few trades
        for i, trade in enumerate(trades[:3]):
            logger.info(f"DEBUG: Trade {i}: {trade.direction} {trade.symbol} pnl={trade.pnl}")
        
        winning_trades = len([t for t in trades if t.pnl > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        total_pnl = sum(t.pnl for t in trades)
        logger.info(f"DEBUG: Total PnL: {total_pnl}")
        total_return_pct = (total_pnl / self.initial_balance * 100) if self.initial_balance > 0 else 0.0
        
        # Simple Sharpe ratio calculation (assuming risk-free rate = 0)
        pnl_list = [t.pnl for t in trades]
        sharpe_ratio = (np.mean(pnl_list) / np.std(pnl_list)) * np.sqrt(252) if len(pnl_list) > 1 and np.std(pnl_list) > 0 else 0.0
        
        metrics = {
            'total_return_pct': total_return_pct,
            'win_rate_pct': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': 0.0,  # Simplified for now
            'total_trades': total_trades
        }
        
        logger.info(f"DEBUG: Calculated metrics: {metrics}")
        return metrics

    def _display_results(self, metrics):
        """Display backtest results"""
        print("=" * 50)
        print("📊 BACKTEST RESULTS")
        print("=" * 50)
        print(f"💰 Total Return: {metrics['total_return_pct']:.2f}%")
        print(f"🎯 Win Rate: {metrics['win_rate_pct']:.2f}%")
        print(f"📈 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"📉 Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"🔄 Total Trades: {metrics['total_trades']}")
        print("=" * 50)