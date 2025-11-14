# Paper Trading Component - API Reference

## 📋 Overview

This document provides a comprehensive API reference for the Paper Trading Component, including all classes, methods, and their parameters, return values, and usage examples.

## 🏗️ Core Classes

### 1. PaperTradingEngine

**File**: `simple_strategy/trading/paper_trading_engine.py`  
**Purpose**: Core paper trading logic and execution engine

#### Class Definition
```python
class PaperTradingEngine:
    def __init__(self, api_account: str, strategy_name: str, simulated_balance: float = 1000.0)

Constructor Parameters 
Parameter
 	
Type
 	
Required
 	
Default
 	
Description
 
 api_account	str	Yes	-	Name of the API account to use for trading 
strategy_name	str	Yes	-	Name of the strategy to load and execute 
simulated_balance	float	No	1000.0	Starting balance for paper trading simulation 
 
  
Instance Attributes 
Attribute
 	
Type
 	
Description
 
 api_account	str	API account name 
strategy_name	str	Strategy name 
simulated_balance	float	Current simulated balance 
initial_balance	float	Initial balance (starting point) 
strategy	object	Loaded strategy object 
is_running	bool	Trading engine status 
trades	list	List of executed trades 
current_positions	dict	Current open positions 
exchange	ccxt.Exchange	Bybit exchange connection 
bybit_balance	float	Actual Bybit demo balance 
 
  
Methods 
initialize_exchange() 

Initialize connection to Bybit exchange. 

Signature: initialize_exchange() -> bool 

Returns: bool - True if connection successful, False otherwise 

Example: 

engine = PaperTradingEngine("Demo Account 1", "Strategy_Mean_Reversion")
if engine.initialize_exchange():
    print("Exchange connection successful")
else:
    print("Exchange connection failed")

Exceptions: 

     FileNotFoundError: API accounts file not found
     KeyError: Account not found in accounts file
     Exception: General connection errors
     

load_strategy() 

Load the specified strategy with optimized parameters. 

Signature: load_strategy() -> bool 

Returns: bool - True if strategy loaded successfully, False otherwise 

Example: 

if engine.load_strategy():
    print("Strategy loaded successfully")
    print(f"Strategy: {engine.strategy}")
else:
    print("Strategy loading failed")

Behavior: 

    Checks for optimized parameters using ParameterManager 
    Imports the strategy module dynamically 
    Loads strategy with optimized or default parameters 
    Sets the strategy object on the engine 

start_trading() 

Start the paper trading session. 

Signature: start_trading() -> bool 

Returns: bool - True if trading started successfully, False otherwise 

Example: 

if engine.start_trading():
    print("Paper trading started")
    while engine.is_running:
        # Monitor trading activity
        pass
else:
    print("Failed to start trading")

if engine.start_trading():
    print("Paper trading started")
    while engine.is_running:
        # Monitor trading activity
        pass
else:
    print("Failed to start trading")

Behavior: 

    Validates strategy and exchange connection 
    Sets is_running flag to True 
    Starts monitoring symbols and executing trades 
    Initializes performance tracking 

execute_buy(symbol, price) 

Execute a buy order for a specified symbol. 

Signature: execute_buy(symbol: str, price: float) -> dict 

Parameters: 
Parameter
 	
Type
 	
Required
 	
Description
 
 symbol	str	Yes	Trading symbol (e.g., "BTCUSDT") 
price	float	Yes	Execution price 
 
  

Returns: dict - Trade execution details 

Example: 

trade = engine.execute_buy("BTCUSDT", 50000.0)
print(f"Buy executed: {trade}")

Trade Structure:

{
    'timestamp': '2025-11-01T10:00:00Z',
    'type': 'BUY',
    'symbol': 'BTCUSDT',
    'price': 50000.0,
    'quantity': 0.001,
    'balance_before': 1000.0,
    'balance_after': 950.0
}

execute_sell(symbol, price) 

Execute a sell order for a specified symbol. 

Signature: execute_sell(symbol: str, price: float) -> dict 

Parameters: 
Parameter
 	
Type
 	
Required
 	
Description
 
 symbol	str	Yes	Trading symbol (e.g., "BTCUSDT") 
price	float	Yes	Execution price 
 
  

Returns: dict - Trade execution details or None if no position to sell 

Example: 

trade = engine.execute_sell("BTCUSDT", 51000.0)
if trade:
    print(f"Sell executed: {trade}")
else:
    print("No position to sell")

calculate_performance_metrics() 

Calculate comprehensive performance metrics. 

Signature: calculate_performance_metrics() -> dict 

Returns: dict - Performance metrics 

Example: 

metrics = engine.calculate_performance_metrics()
print(f"Win Rate: {metrics['win_rate']:.2f}%")
print(f"Total Return: {metrics['total_return']:.2f}%")
print(f"Profit Factor: {metrics['profit_factor']:.2f}")

Metrics Structure:

{
    'total_trades': int,
    'winning_trades': int,
    'win_rate': float,
    'total_pnl': float,
    'total_return': float,
    'avg_profit': float,
    'avg_loss': float,
    'profit_factor': float,
    'current_balance': float,
    'initial_balance': float
}

2. PaperTradingLauncher 

File: simple_strategy/trading/paper_trading_launcher.py
Purpose: GUI interface for paper trading 
Class Definition 

class PaperTradingLauncher:
    def __init__(self, api_account: str = None, strategy_name: str = None, simulated_balance: float = None)

Constructor Parameters 
Parameter
 	
Type
 	
Required
 	
Default
 	
Description
 
 api_account	str	No	None	API account name (uses default if None) 
strategy_name	str	No	None	Strategy name (uses default if None) 
simulated_balance	float	No	None	Simulated balance (uses default if None) 
 
  
Methods 
create_widgets() 

Create all GUI widgets and interface elements. 

Signature: create_widgets() -> None 

Behavior: 

    Creates header frame with title 
    Creates account information display 
    Creates parameter status indicator 
    Creates control buttons (Start/Stop) 
    Creates trading log display 
    Creates performance summary display 

start_trading() 

Start paper trading from GUI. 

Signature: start_trading() -> None 

Behavior: 

    Checks for optimized parameters 
    Prompts user if no optimized parameters found 
    Initializes PaperTradingEngine 
    Starts trading session 
    Updates GUI controls and status 

stop_trading() 

Stop paper trading from GUI. 

Signature: stop_trading() -> None 

Behavior: 

    Stops trading engine 
    Updates GUI controls and status 
    Logs final performance metrics 

log_message(message) 

Add message to trading log. 

Signature: log_message(message: str) -> None 

Parameters: 
Parameter
 	
Type
 	
Required
 	
Description
 
 message	str	Yes	Message to log 
 
  

Example: 

launcher.log_message("Trade executed: BUY BTCUSDT @ 50000")

update_performance() 

Update performance display in GUI. 

Signature: update_performance() -> None 

Behavior: 

    Calculates current performance metrics 
    Updates performance text widget 
    Formats metrics for display 

📊 Data Structures 
Trade Record 

{
    'timestamp': str,        # ISO format timestamp
    'type': str,            # 'BUY' or 'SELL'
    'symbol': str,          # Trading symbol
    'price': float,         # Execution price
    'quantity': float,      # Trade quantity
    'balance_before': float, # Balance before trade
    'balance_after': float   # Balance after trade
}

Position Record

{
    'symbol': str,          # Trading symbol
    'quantity': float,      # Current position quantity
    'entry_price': float,   # Average entry price
    'stop_loss': float,     # Stop loss price
    'take_profit': float    # Take profit price
}

Performance Metrics

{
    'total_trades': int,          # Total number of trades
    'winning_trades': int,        # Number of winning trades
    'win_rate': float,            # Win rate percentage
    'total_pnl': float,           # Total profit/loss
    'total_return': float,        # Total return percentage
    'avg_profit': float,          # Average profit per trade
    'avg_loss': float,            # Average loss per trade
    'profit_factor': float,       # Profit factor ratio
    'current_balance': float,     # Current simulated balance
    'initial_balance': float      # Initial balance
}

🔧 Integration Examples 
Basic Usage 

from simple_strategy.trading.paper_trading_engine import PaperTradingEngine

# Initialize engine
engine = PaperTradingEngine(
    api_account="Demo Account 1",
    strategy_name="Strategy_Mean_Reversion",
    simulated_balance=1000.0
)

# Setup
if engine.initialize_exchange() and engine.load_strategy():
    # Start trading
    engine.start_trading()
    
    # Monitor performance
    while engine.is_running:
        metrics = engine.calculate_performance_metrics()
        print(f"Current Balance: ${metrics['current_balance']:.2f}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        time.sleep(60)  # Check every minute

GUI Usage

from simple_strategy.trading.paper_trading_launcher import PaperTradingLauncher

# Launch GUI
launcher = PaperTradingLauncher(
    api_account="Demo Account 1",
    strategy_name="Strategy_Mean_Reversion",
    simulated_balance=1000.0
)

# Start GUI event loop
launcher.root.mainloop()

Strategy Integration

# Strategy file example: simple_strategy/strategies/Strategy_Mean_Reversion.py
def create_strategy(rsi_period=14, rsi_oversold=30, rsi_overbought=70, position_size=0.1):
    """Create mean reversion strategy"""
    from simple_strategy.strategies.strategy_builder import StrategyBuilder
    from simple_strategy.strategies.indicators_library import rsi
    from simple_strategy.strategies.signals_library import overbought_oversold
    
    # Create strategy builder
    strategy = StrategyBuilder(['BTCUSDT'], ['1m'])
    
    # Add indicators
    strategy.add_indicator('rsi', rsi, period=rsi_period)
    
    # Add signals
    strategy.add_signal_rule('rsi_signal', overbought_oversold, 
                            oversold=rsi_oversold, overbought=rsi_overbought)
    
    # Set position sizing
    strategy.set_position_size(position_size)
    
    return strategy.build()

Performance Monitoring

def monitor_performance(engine):
    """Monitor and display performance metrics"""
    metrics = engine.calculate_performance_metrics()
    
    print("=== Performance Summary ===")
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Win Rate: {metrics['win_rate']:.2f}%")
    print(f"Total Return: {metrics['total_return']:.2f}%")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"Current Balance: ${metrics['current_balance']:.2f}")
    print(f"Initial Balance: ${metrics['initial_balance']:.2f}")
    
    # Trade breakdown
    print("\n=== Recent Trades ===")
    for trade in engine.trades[-5:]:  # Show last 5 trades
        print(f"{trade['timestamp']} | {trade['type']} {trade['symbol']} @ {trade['price']}")

🚨 Error Handling 
Common Exceptions 
API Connection Errors 

try:
    engine.initialize_exchange()
except Exception as e:
    print(f"API Connection Error: {e}")
    # Check API credentials and network connection

Strategy Loading Errors

try:
    engine.load_strategy()
except ImportError as e:
    print(f"Strategy Import Error: {e}")
    # Check strategy file exists and has correct structure
except AttributeError as e:
    print(f"Strategy Structure Error: {e}")
    # Check strategy has create_strategy function

Trade Execution Errors

try:
    trade = engine.execute_buy("BTCUSDT", 50000.0)
except Exception as e:
    print(f"Trade Execution Error: {e}")
    # Check symbol exists and price is valid

Validation Methods 
Validate API Account 

def validate_api_account(account_name):
    """Validate API account configuration"""
    import os
    import json
    
    try:
        api_accounts_file = os.path.join(
            os.path.dirname(__file__), 'api_accounts.json'
        )
        
        with open(api_accounts_file, 'r') as f:
            accounts = json.load(f)
        
        # Check account exists
        for account_type in ['demo_accounts', 'live_accounts']:
            if account_name in accounts.get(account_type, {}):
                account_info = accounts[account_type][account_name]
                
                # Validate required fields
                required_fields = ['api_key', 'api_secret']
                for field in required_fields:
                    if field not in account_info:
                        return False, f"Missing {field} in account configuration"
                
                return True, "Account valid"
        
        return False, "Account not found"
        
    except FileNotFoundError:
        return False, "API accounts file not found"
    except Exception as e:
        return False, f"Validation error: {e}"

Validate Strategy

def validate_strategy(strategy_name):
    """Validate strategy file structure"""
    try:
        # Import strategy module
        strategy_module = __import__(
            f'simple_strategy.strategies.{strategy_name}', 
            fromlist=['']
        )
        
        # Check required function exists
        if not hasattr(strategy_module, 'create_strategy'):
            return False, "Strategy missing create_strategy function"
        
        # Test strategy creation
        try:
            strategy = strategy_module.create_strategy()
            if strategy is None:
                return False, "Strategy creation returned None"
        except Exception as e:
            return False, f"Strategy creation failed: {e}"
        
        return True, "Strategy valid"
        
    except ImportError as e:
        return False, f"Strategy import failed: {e}"
    except Exception as e:
        return False, f"Strategy validation error: {e}"

📝 Best Practices 
1. Error Handling 

# Always check return values
if not engine.initialize_exchange():
    print("Failed to initialize exchange")
    return

if not engine.load_strategy():
    print("Failed to load strategy")
    return

2. Resource Management

# Clean up resources when done
try:
    engine.start_trading()
    # Monitor trading
finally:
    engine.stop_trading()

3. Performance Monitoring

# Monitor performance regularly
import time

while engine.is_running:
    metrics = engine.calculate_performance_metrics()
    
    # Check for performance issues
    if metrics['win_rate'] < 50:
        print("Warning: Low win rate detected")
    
    if metrics['total_return'] < -10:
        print("Warning: Significant losses detected")
        engine.stop_trading()
        break
    
    time.sleep(300)  # Check every 5 minutes

4. Logging

# Use the logging system for debugging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Starting paper trading with {engine.strategy_name}")
logger.info(f"Initial balance: ${engine.simulated_balance}")

API Reference Version: 1.0
Component Status: 70% Complete
Last Updated: November 2025
