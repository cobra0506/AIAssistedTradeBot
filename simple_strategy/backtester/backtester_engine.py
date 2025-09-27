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
from pathlib import Path
import sys

# Fix import paths - shared is a sibling directory, not a subdirectory
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.data_feeder import DataFeeder
from shared.strategy_base import StrategyBase

# Configure logging to reduce debug output
import logging
logging.basicConfig(
    level=logging.INFO,  # Change from DEBUG to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Specifically set debug level for backtester to INFO
logging.getLogger('simple_strategy.backtester.backtester_engine').setLevel(logging.INFO)
logging.getLogger('simple_strategy.strategies.strategy_builder').setLevel(logging.INFO)

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
    
    def run_backtest(self, symbols: List[str], timeframes: List[str],
                     start_date: Union[str, datetime], 
                     end_date: Union[str, datetime]) -> Dict[str, Any]:
        """
        Run complete backtest for specified parameters
        
        Args:
            symbols: List of trading symbols
            timeframes: List of timeframes
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest for symbols: {symbols}, timeframes: {timeframes}")
        logger.info(f"Date range: {start_date} to {end_date}")
        
        # Initialize backtest
        self.start_time = time.time()
        self.is_running = True
        
        try:
            # Load data using DataFeeder
            if not self.data_feeder.load_data(symbols, timeframes, start_date, end_date):
                raise RuntimeError("Failed to load data for backtest")

            # DEBUG: Check what data was loaded
            print(f"🔧 DEBUG: Data cache after load: {list(self.data_feeder.data_cache.keys())}")
            for symbol in symbols:
                if symbol in self.data_feeder.data_cache:
                    print(f"🔧 DEBUG: {symbol} timeframes: {list(self.data_feeder.data_cache[symbol].keys())}")
                    for timeframe in timeframes:
                        if timeframe in self.data_feeder.data_cache[symbol]:
                            df = self.data_feeder.data_cache[symbol][timeframe]
                            print(f"🔧 DEBUG: {symbol} {timeframe} shape: {df.shape}, date range: {df.index.min()} to {df.index.max()}")

            # Get loaded data
            all_data = self.data_feeder.get_data_for_symbols(symbols, timeframes, start_date, end_date)
            
            # Validate data
            if not self._validate_data(all_data, symbols, timeframes):
                raise RuntimeError("Data validation failed")
            
            # Process data chronologically
            results = self._process_data_chronologically(all_data, symbols, timeframes)
            
            # Calculate final results
            final_results = self._calculate_final_results(results)
            
            self.end_time = time.time()
            self.is_running = False
            
            logger.info(f"Backtest completed in {self.end_time - self.start_time:.2f} seconds")
            return final_results
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            self.is_running = False
            return {'error': str(e)}
    
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
            print(f"🔧 DEBUG: _process_data_chronologically called")
            
            # Get all unique timestamps across all symbols and timeframes
            all_timestamps = set()
            for symbol in symbols:
                for timeframe in timeframes:
                    if symbol in data and timeframe in data[symbol]:
                        all_timestamps.update(data[symbol][timeframe].index)
            
            # Sort timestamps chronologically
            sorted_timestamps = sorted(all_timestamps)
            print(f"🔧 DEBUG: Processing {len(sorted_timestamps)} timestamps")
            
            # Initialize results tracking
            results = {
                'equity_curve': [],
                'trades': [],
                'signals': [],
                'timestamps': [],
                'portfolio_values': []
            }
            
            # Process each timestamp
            for i, timestamp in enumerate(sorted_timestamps):
                if not self.is_running:
                    print("🔧 DEBUG: Backtest stopped during processing")
                    break
                
                # Get data for current timestamp across all symbols and timeframes
                current_data = self._get_data_for_timestamp(data, symbols, timeframes, timestamp)
                
                # Generate signals using strategy
                signals = self.strategy.generate_signals(current_data)
                
                # Process signals and execute trades
                trade_results = self._process_signals(signals, current_data, timestamp)
                
                # Update results
                self._update_results(results, signals, trade_results, timestamp)
                
                # Update processing stats
                self.processing_stats['total_rows_processed'] += len(symbols) * len(timeframes)
                self.processing_stats['total_signals_generated'] += len([s for s in signals.values() if s != 'HOLD'])
                
                # Log progress
                if i % 1000 == 0:
                    progress = (i / len(sorted_timestamps)) * 100
                    print(f"🔧 DEBUG: Processing progress: {progress:.1f}%")
            
            print(f"🔧 DEBUG: Processing complete. Generated {len(results['trades'])} trades")
            return results
        except Exception as e:
            print(f"🔧 DEBUG: Error in _process_data_chronologically: {e}")
            import traceback
            print(f"🔧 DEBUG: Full traceback: {traceback.format_exc()}")
            return {'error': str(e)}
    
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
            Data dictionary for the specific timestamp
        """
        timestamp_data = {}
        
        for symbol in symbols:
            timestamp_data[symbol] = {}
            for timeframe in timeframes:
                df = data[symbol][timeframe]
                
                # Get data up to current timestamp
                mask = df.index <= timestamp
                historical_data = df[mask].copy()
                
                timestamp_data[symbol][timeframe] = historical_data
        
        return timestamp_data
    
    def _process_signals(self, signals: Dict[str, Dict[str, str]], current_data: Dict[str, Dict[str, pd.DataFrame]], timestamp: datetime) -> List[Dict[str, Any]]:
        """Process signals and execute trades"""
        trade_results = []
        
        try:
            for symbol, timeframe_signals in signals.items():
                for timeframe, signal in timeframe_signals.items():
                    if signal in ['BUY', 'SELL']:
                        # Check if we can execute this trade
                        if self._can_execute_trade(symbol, signal, timestamp):
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
            # Get the first timeframe data for this symbol
            if symbol not in current_data or not current_data[symbol]:
                logger.warning(f"⚠️ No data available for {symbol}")
                return 0.0
            
            # Get the first timeframe DataFrame
            timeframe_data = list(current_data[symbol].values())[0]
            
            if timeframe_data.empty:
                logger.warning(f"⚠️ Empty data for {symbol}")
                return 0.0
            
            # Get the last close price
            current_price = timeframe_data['close'].iloc[-1]
            
            return float(current_price)
            
        except Exception as e:
            logger.error(f"❌ Error getting current price for {symbol}: {e}")
            return 0.0
    
    def _execute_trade(self, symbol: str, signal: str, timestamp: datetime, current_data: Dict[str, Dict[str, pd.DataFrame]]) -> Dict[str, Any]:
        """Execute a trade based on signal"""
        try:
            # Get current price
            current_price = self._get_current_price(symbol, current_data)
            
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
            elif signal == 'SELL':
                self.strategy.balance += trade_cost
            
            logger.info(f"✅ Executed {signal} trade: {position_size} {symbol} at ${current_price:.2f}")
            
            return trade_result
            
        except Exception as e:
            logger.error(f"❌ Error executing trade for {symbol}: {e}")
            return {'executed': False, 'reason': str(e)}
    
    def _update_results(self, results: Dict[str, Any], signals: Dict[str, Dict[str, str]], 
                       trades: List[Dict[str, Any]], timestamp: datetime):
        """
        Update results dictionary with current state
        
        Args:
            results: Results dictionary to update
            signals: Current signals
            trades: Executed trades
            timestamp: Current timestamp
        """
        # Calculate current portfolio value
        portfolio_value = self.strategy.balance
        for symbol, position in self.strategy.positions.items():
            # For simplicity, use entry price (in real implementation, would use current price)
            portfolio_value += position['size'] * position['entry_price']
        
        # Update results
        results['equity_curve'].append({
            'timestamp': timestamp,
            'balance': self.strategy.balance,
            'portfolio_value': portfolio_value
        })
        
        results['signals'].append({
            'timestamp': timestamp,
            'signals': signals
        })
        
        results['timestamps'].append(timestamp)
        results['portfolio_values'].append(portfolio_value)
        
        # Add trades
        results['trades'].extend(trades)
    
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
                initial_equity = final_results['equity_curve'][0] if final_results['equity_curve'] else 10000
                final_equity = final_results['equity_curve'][-1] if final_results['equity_curve'] else initial_equity
                
                total_return = (final_equity - initial_equity) / initial_equity
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