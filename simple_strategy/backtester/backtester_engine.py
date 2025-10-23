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
        
        logger.info(f"BacktesterEngine initialized with strategy: {strategy.name}")
        logger.info(f"Risk management {'enabled' if self.risk_manager else 'disabled'}")
    
    def run_backtest(self, strategy=None, data=None, start_date=None, end_date=None, 
                 initial_balance=10000, symbols=None, timeframes=None, config=None):
        """
        Run backtest with enhanced progress reporting
        Compatible with GUI calling convention
        """
        try:
            # If strategy is None, use self.strategy
            if strategy is None:
                strategy = self.strategy
            
            # If data is None, load it using data_feeder
            if data is None:
                data = self.data_feeder.get_data_for_symbols(
                    symbols or self.strategy.symbols, 
                    timeframes or self.strategy.timeframes,
                    start_date or datetime.now() - timedelta(days=30),
                    end_date or datetime.now()
                )
            
            # Initialize variables
            self.trades = []
            self.balance = initial_balance
            self.initial_balance = initial_balance
            
            # Calculate total processing steps for progress tracking
            total_steps = 0
            for symbol in data:
                for timeframe in data[symbol]:
                    df = data[symbol][timeframe]
                    total_steps += len(df)
            
            processed_steps = 0
            last_progress_update = 0
            
            logger.info(f"🔧 Starting backtest with {total_steps} total data points")
            
            # Process each symbol and timeframe
            for symbol in data:
                for timeframe in data[symbol]:
                    df = data[symbol][timeframe].copy()
                    
                    logger.info(f"🔧 Processing {symbol} {timeframe}: {len(df)} rows")
                    
                    # Process each row
                    for i, (timestamp, row) in enumerate(df.iterrows()):
                        # Create the proper data structure for signal generation
                        current_data = {symbol: {timeframe: df.loc[:timestamp]}}
                        
                        # Generate signals
                        signals = strategy.generate_signals(current_data)
                        
                        # Execute trades based on signals
                        signal = signals[symbol][timeframe]
                        if signal in ['BUY', 'SELL']:
                            # Create proper data structure for trade execution
                            trade_data = {symbol: {timeframe: df.loc[:timestamp]}}
                            trade_result = self._execute_trade(symbol, signal, timestamp, trade_data)
                            if trade_result.get('executed', False):
                                # Calculate PnL for the trade
                                if signal == 'SELL':
                                    # For SELL trades, calculate PnL based on entry price
                                    entry_price = trade_result.get('entry_price', row['close'])
                                    exit_price = row['close']
                                    quantity = trade_result.get('quantity', 0)
                                    pnl = (exit_price - entry_price) * quantity
                                    trade_result['pnl'] = pnl
                                    trade_result['balance_after'] = self.balance
                                else:
                                    # For BUY trades, just track the entry
                                    trade_result['entry_price'] = row['close']
                                    trade_result['pnl'] = 0
                                    trade_result['balance_after'] = self.balance
                        
                        # Update progress
                        processed_steps += 1
                        progress_percent = (processed_steps / total_steps) * 100
                        
                        # Update progress every 5% or for the last update
                        if progress_percent - last_progress_update >= 5 or progress_percent == 100:
                            logger.info(f"🔧 Backtest progress: {progress_percent:.1f}%")
                            last_progress_update = progress_percent
                    
                    logger.info(f"🔧 Completed {symbol} {timeframe}")
            
            # Calculate final metrics
            final_balance = self.balance
            performance_metrics = self.calculate_performance_metrics(
                self.trades, self.initial_balance, final_balance
            )
            
            # Display results
            self.display_results(performance_metrics)
            
            return performance_metrics
            
        except Exception as e:
            logger.error(f"❌ Error during backtest: {e}")
            raise
    
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