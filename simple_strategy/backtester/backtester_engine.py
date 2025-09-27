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

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    
    def _process_signals(self, signals: Dict[str, Dict[str, str]], 
                        current_data: Dict[str, Dict[str, pd.DataFrame]], 
                        timestamp: datetime) -> List[Dict[str, Any]]:
        """
        Process strategy signals and execute trades
        
        Args:
            signals: Signals from strategy
            current_data: Current market data
            timestamp: Current timestamp
            
        Returns:
            List of executed trades
        """
        trades = []
        
        for symbol, timeframe_signals in signals.items():
            for timeframe, signal in timeframe_signals.items():
                if signal == 'HOLD':
                    continue
                
                # Get current price
                current_price = self._get_current_price(current_data[symbol][timeframe])
                
                if current_price is None:
                    logger.warning(f"Could not get current price for {symbol} at {timestamp}")
                    continue
                
                # Validate signal
                if not self.strategy.validate_signal(symbol, signal, current_data[symbol][timeframe]):
                    logger.warning(f"Signal validation failed for {symbol}: {signal}")
                    continue
                
                # Calculate position size
                position_size = self.strategy.calculate_position_size(symbol)
                
                # Execute trade
                trade = self._execute_trade(symbol, signal, position_size, current_price, timestamp)
                if trade:
                    trades.append(trade)
                    self.processing_stats['total_trades_executed'] += 1
        
        return trades
    
    def _get_current_price(self, df: pd.DataFrame) -> Optional[float]:
        """Get current price from DataFrame"""
        if df.empty:
            print(f"🔧 DEBUG: _get_current_price: DataFrame is empty")
            return None
        
        # Use the last available close price
        price = df['close'].iloc[-1]
        print(f"🔧 DEBUG: _get_current_price: {price}")
        return price
    
    def _execute_trade(self, symbol: str, signal: str, position_size: float,
                  price: float, timestamp: datetime) -> Optional[Dict[str, Any]]:
        """Execute a trade"""
        try:
            print(f"🔧 DEBUG: _execute_trade called with symbol={symbol}, signal={signal}, position_size={position_size}, price={price}")
            
            trade = {
                'symbol': symbol,
                'signal': signal,
                'position_size': position_size,
                'price': price,
                'timestamp': timestamp,
                'trade_id': f"{symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{np.random.randint(1000, 9999)}"
            }
            
            # Update strategy state
            if signal == 'BUY':
                # Open long position
                cost = position_size * price
                print(f"🔧 DEBUG: BUY trade - cost={cost}, available balance={self.strategy.balance}")
                
                if cost <= self.strategy.balance:
                    self.strategy.balance -= cost
                    self.strategy.positions[symbol] = {
                        'direction': 'long',
                        'size': position_size,
                        'entry_price': price,
                        'entry_timestamp': timestamp
                    }
                    print(f"🔧 DEBUG: Executed BUY for {symbol}: size={position_size}, price={price}")
                else:
                    print(f"🔧 DEBUG: Insufficient balance for {symbol} BUY: needed={cost}, available={self.strategy.balance}")
                    return None
                    
            elif signal == 'SELL':
                # Close position if exists
                if symbol in self.strategy.positions:
                    position = self.strategy.positions[symbol]
                    print(f"🔧 DEBUG: SELL trade - closing position: {position}")
                    
                    if position['direction'] == 'long':
                        # Calculate profit/loss
                        profit_loss = (price - position['entry_price']) * position['size']
                        print(f"🔧 DEBUG: Profit/Loss calculation: ({price} - {position['entry_price']}) * {position['size']} = {profit_loss}")
                        
                        # Update balance
                        self.strategy.balance += position_size * price
                        print(f"🔧 DEBUG: Updated balance: {self.strategy.balance}")
                        
                        # Remove position
                        del self.strategy.positions[symbol]
                        
                        # Add profit/loss to trade
                        trade['profit_loss'] = profit_loss
                        trade['entry_price'] = position['entry_price']
                        trade['entry_timestamp'] = position['entry_timestamp']
                        
                        print(f"🔧 DEBUG: Executed SELL for {symbol}: size={position_size}, price={price}, P&L={profit_loss}")
                    else:
                        print(f"🔧 DEBUG: Unknown position direction: {position['direction']}")
                        return None
                else:
                    print(f"🔧 DEBUG: No position to close for {symbol}")
                    return None
                    
            return trade
        except Exception as e:
            print(f"🔧 DEBUG: Error in _execute_trade: {e}")
            import traceback
            print(f"🔧 DEBUG: Full traceback: {traceback.format_exc()}")
            return None
    
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
        """Calculate final backtest results"""
        try:
            print(f"🔧 DEBUG: _calculate_final_results called with keys: {list(results.keys())}")
            
            # Calculate summary statistics
            total_trades = len(results['trades'])
            print(f"🔧 DEBUG: Total trades: {total_trades}")
            
            # Calculate profit/loss
            total_pnl = 0
            winning_trades = 0
            losing_trades = 0
            
            for trade in results['trades']:
                if 'profit_loss' in trade:
                    pnl = trade['profit_loss']
                    print(f"🔧 DEBUG: Processing trade P&L: {pnl}")
                    
                    # Check if pnl is None
                    if pnl is None:
                        print(f"🔧 DEBUG: WARNING: Trade P&L is None!")
                        continue
                        
                    total_pnl += pnl
                    
                    if pnl > 0:
                        winning_trades += 1
                    elif pnl < 0:
                        losing_trades += 1
            
            print(f"🔧 DEBUG: Total P&L: {total_pnl}")
            
            # Calculate win rate
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            print(f"🔧 DEBUG: Win rate: {win_rate}")
            
            # Create summary
            summary = {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'initial_balance': self.strategy.initial_balance,
                'final_balance': self.strategy.balance,
                'balance_change': self.strategy.balance - self.strategy.initial_balance
            }
            
            print(f"🔧 DEBUG: Summary: {summary}")
            
            # Return final results
            final_results = {
                'summary': summary,
                'trades': results['trades'],
                'equity_curve': results['equity_curve'],
                'signals': results['signals'],
                'processing_stats': self.processing_stats
            }
            
            return final_results
        except Exception as e:
            print(f"🔧 DEBUG: Error in _calculate_final_results: {e}")
            import traceback
            print(f"🔧 DEBUG: Full traceback: {traceback.format_exc()}")
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