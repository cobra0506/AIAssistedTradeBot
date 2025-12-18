import os
import json
import time
import requests
import hmac
import hashlib
import numpy as np
import pandas as pd
import time
from urllib.parse import urlencode
from datetime import datetime
from datetime import timedelta
from simple_strategy.shared.data_feeder import DataFeeder
# Removed unused imports to avoid circular dependencies
import asyncio
#from shared_modules.data_collection.hybrid_system import HybridTradingSystem
#from shared_modules.data_collection.config import DataCollectionConfig

class PaperTradingEngine:
    def __init__(self, api_account, strategy_name, initial_balance=1000, log_callback=None, status_callback=None, performance_callback=None):
        self.api_account = api_account
        self.strategy_name = strategy_name
        self.initial_balance = float(initial_balance)  # This is your working capital
        self.working_capital = self.initial_balance  # Track working capital separately
        self.real_balance = 0.0
        self.balance_offset = 0.0
        
        # API configuration - using the EXACT working configuration
        self.api_key = None
        self.api_secret = None
        self.base_url = "https://api-demo.bybit.com"
        self.recv_window = "5000"
        
        # Trading state
        self.is_running = False
        self.trades = []
        self.current_positions = {}
        self.strategy = None
        
        # Data feeder for strategy integration (keep for compatibility)
        # Get the absolute path to the project's root 'data' folder
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, 'data')
        self.data_feeder = DataFeeder(data_dir=data_dir)
        
        # GUI callback functions
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.performance_callback = performance_callback
        
        # NEW: Use shared data access instead of creating new data collection
        # Initialize this later to avoid recursion issues
        self.shared_data_access = None

        # Add these missing attributes
        self.data_system_initialized = False
        self.is_running = False
        self.trading_loop_active = False
        
        # Use symbols from data collection config
        #from shared_modules.data_collection.config import DataCollectionConfig
        #self.data_config = DataCollectionConfig()
        #self.symbols_to_collect = self.data_config.SYMBOLS if not self.data_config.FETCH_ALL_SYMBOLS else None
        
        self.log_message(f"Paper Trading Engine initialized:")
        self.log_message(f"  Account: {api_account}")
        self.log_message(f"  Strategy: {strategy_name}")
        self.log_message(f"  Initial Balance: ${self.initial_balance}")
        
        # Load credentials and test connection
        self.load_credentials()
        self.test_connection()
        
        # Get real balance and calculate offset
        self.real_balance = self.get_real_balance()
        self.balance_offset = self.real_balance - self.initial_balance
        self.log_message(f"  Real Balance: ${self.real_balance}")
        self.log_message(f"  Balance Offset: ${self.balance_offset}")

    def get_working_capital(self):
        """Get current working capital for position sizing"""
        # Calculate realized P&L
        realized_pnl = 0.0
        for trade in self.trades:
            if trade['type'] == 'SELL':
                # For simplicity, assume P&L is stored in the trade record
                if 'pnl' in trade:
                    realized_pnl += trade['pnl']
        
        # Working capital = initial - realized P&L
        working_capital = self.initial_balance - realized_pnl
        return working_capital

    def update_working_capital_after_trade(self, trade_pnl):
        """Update working capital after a trade"""
        # Adjust working capital by the P&L of the trade
        self.working_capital += trade_pnl

    def log_message(self, message):
        """Log message to both console and GUI if available"""
        print(message)  # Use print instead of self.log_message()
        if self.log_callback:
            self.log_callback(message)

    def initialize_shared_data_access(self):
        """Initialize shared data access safely"""
        try:
            from shared_modules.data_collection.shared_data_access import SharedDataAccess
            self.shared_data_access = SharedDataAccess()
            
            # Check if data collection is running
            if self.shared_data_access.is_data_collection_running():
                self.log_message("✅ Using existing data collection process")
            else:
                self.log_message("⚠️ Data collection not running - will use existing CSV files")
                
            return True
        except Exception as e:
            self.log_message(f"❌ Error initializing shared data access: {e}")
            return False
    
    def load_credentials(self):
        """Load API credentials from file"""
        try:
            api_accounts_file = os.path.join(os.path.dirname(__file__), 'api_accounts.json')
            with open(api_accounts_file, 'r') as f:
                accounts = json.load(f)
            
            # Find the selected account
            for account_type in ['demo_accounts', 'live_accounts']:
                if self.api_account in accounts.get(account_type, {}):
                    account_info = accounts[account_type][self.api_account]
                    self.api_key = account_info['api_key']
                    self.api_secret = account_info['api_secret']
                    self.log_message(f"✅ API credentials loaded for {self.api_account}")
                    return True
            
            self.log_message(f"❌ Account '{self.api_account}' not found")
            return False
            
        except Exception as e:
            self.log_message(f"❌ Error loading API credentials: {e}")
            return False
    
    def generate_signature(self, timestamp, method, path, body='', params=None):
        """Generate HMAC-SHA256 signature - EXACT working method"""
        if method == "GET" and params:
            sorted_params = sorted(params.items())
            query_string = urlencode(sorted_params)
            param_str = timestamp + self.api_key + self.recv_window + query_string
        elif method == "POST" and body:
            if isinstance(body, dict):
                import json
                body_str = json.dumps(body, separators=(',', ':'), sort_keys=True)
                param_str = timestamp + self.api_key + self.recv_window + body_str
            else:
                param_str = timestamp + self.api_key + self.recv_window + str(body)
        else:
            param_str = timestamp + self.api_key + self.recv_window + str(body)
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def make_request(self, method, path, params=None, data=None):
        """Make authenticated request - EXACT working method"""
        try:
            # Handle query parameters
            if params:
                query_string = urlencode(params)
                url = f"{self.base_url}{path}?{query_string}"
            else:
                url = f"{self.base_url}{path}"
            
            headers = {"Content-Type": "application/json"}
            
            # Add authentication
            timestamp = str(int(time.time() * 1000))
            signature = self.generate_signature(timestamp, method, path, body=data, params=params)
            
            headers.update({
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-RECV-WINDOW": self.recv_window,
                "X-BAPI-SIGN": signature
            })
            
            # Make request
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if isinstance(data, dict):
                    import json
                    body_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
                    response = requests.post(url, headers=headers, data=body_str)
                else:
                    response = requests.post(url, headers=headers, json=data)
            
            result = response.json()
            
            if response.status_code == 200 and result.get('retCode') == 0:
                return result['result'], None
            else:
                error_msg = result.get('retMsg', 'Unknown error')
                return None, error_msg
                
        except Exception as e:
            return None, str(e)
        
    def get_market_data(self, symbol, timeframe, limit=100):
        """Get market data from shared data access"""
        if self.shared_data_access:
            return self.shared_data_access.get_latest_data(symbol, timeframe, limit=limit)
        else:
            # Fallback to empty list if shared data access not available
            self.log_message(f"⚠️ Shared data access not available for {symbol}_{timeframe}")
            return []
    
    def test_connection(self):
        """Test the connection - EXACT working method"""
        try:
            self.log_message("Testing connection...")
            result, error = self.make_request("GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"})
            
            if error:
                self.log_message(f"❌ Connection test failed: {error}")
                return False
            
            if result and 'list' in result and result['list']:
                wallet_data = result['list'][0]
                balance = float(wallet_data.get('totalAvailableBalance', '0'))
                self.log_message(f"✅ Connection successful! Balance: ${balance}")
                return True
            else:
                self.log_message("❌ Connection test failed: Invalid response format")
                return False
                
        except Exception as e:
            self.log_message(f"❌ Connection test error: {e}")
            return False
    
    def get_balance(self):
        """Get current simulated balance (for compatibility)"""
        return self.get_display_balance()

    def get_real_balance(self):
        """Get actual balance from Bybit"""
        try:
            result, error = self.make_request("GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"})
            if error:
                self.log_message(f"❌ Error getting real balance: {error}")
                return 0
            if result and 'list' in result and result['list']:
                wallet_data = result['list'][0]
                balance = float(wallet_data.get('totalAvailableBalance', '0'))
                return balance
            else:
                return 0
        except Exception as e:
            self.log_message(f"❌ Error getting real balance: {e}")
            return 0

    def get_display_balance(self):
        """Get the simulated balance for display"""
        return self.simulated_balance
    
    def get_all_perpetual_symbols(self):
        """Get all perpetual symbols"""
        try:
            result, error = self.make_request("GET", "/v5/market/instruments-info", params={"category": "linear", "limit": 1000})
            
            if error:
                self.log_message(f"❌ Error getting symbols: {error}")
                return []
            
            symbols = []
            excluded_symbols = ['USDC', 'USDE', 'USTC']
            
            for instrument in result['list']:
                symbol = instrument.get('symbol', '')
                if (not any(excl in symbol for excl in excluded_symbols) and
                    "-" not in symbol and
                    symbol.endswith('USDT') and
                    instrument.get('contractType') == 'LinearPerpetual' and
                    instrument.get('status') == 'Trading'):
                    symbols.append(symbol)
            
            self.log_message(f"✅ Found {len(symbols)} perpetual symbols")
            return sorted(symbols)
                
        except Exception as e:
            self.log_message(f"❌ Error getting symbols: {e}")
            return []
        
    def filter_tradable_symbols(self, all_symbols):
        """Filter symbols to only include tradable ones"""
        tradable_symbols = []
        
        for symbol in all_symbols:
            # Filter out obvious non-tradable symbols
            if any(skip in symbol.upper() for skip in ['1000', '10000', '1000000', 'BABY', 'CHEEMS', 'MOG', 'ELON', 'QUBIC', 'SATS', 'BONK', 'BTT', 'CAT']):
                continue
            
            # Only include major symbols with good liquidity
            if symbol.endswith('USDT') and len(symbol) <= 10:  # Reasonable symbol length
                tradable_symbols.append(symbol)
        
        self.log_message(f"📊 Filtered {len(all_symbols)} symbols down to {len(tradable_symbols)} tradable symbols")
        return tradable_symbols
    
    def execute_buy(self, symbol, quantity=None):
        """Execute a buy order"""
        if quantity is None:
            quantity = self.calculate_position_size(symbol)
        
        try:
            # Get current price to calculate minimum order value
            current_price = self.get_current_price_from_api(symbol)
            if current_price <= 0:
                self.log_message(f"❌ Could not get current price for {symbol}")
                return None
            
            # Calculate minimum order value (typically $1 minimum on Bybit)
            min_order_value = 1.0
            min_quantity = min_order_value / current_price
            
            # Use 5% of working capital for position sizing
            working_capital = self.get_working_capital()
            position_value = working_capital * 0.05
            calculated_quantity = position_value / current_price
            
            # Use the larger of our calculated quantity or the minimum required
            final_quantity = max(calculated_quantity, min_quantity)
            
            # Log what we're doing
            self.log_message(f"📊 Position sizing: 5% of working capital = ${position_value:.2f}, calculated qty = {calculated_quantity:.6f}, min required = {min_quantity:.6f}")
            
            # Create order data with properly formatted quantity
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": "Buy",
                "orderType": "Market",
                "qty": f"{final_quantity:.6f}",  # Format to 6 decimal places
                "timeInForce": "GTC"
            }
            
            self.log_message(f"📈 Placing BUY order for {final_quantity} {symbol}...")
            result, error = self.make_request("POST", "/v5/order/create", data=order_data)
            
            if error:
                self.log_message(f"❌ Buy order failed: {error}")
                return None
            
            # Record the trade
            trade = {
                'timestamp': datetime.now().isoformat(),
                'type': 'BUY',
                'symbol': symbol,
                'quantity': final_quantity,
                'order_id': result.get('orderId'),
                'status': result.get('orderStatus', 'Unknown')
            }
            
            self.trades.append(trade)
            self.current_positions[symbol] = {
                'quantity': final_quantity,
                'order_id': result.get('orderId'),
                'entry_time': datetime.now().isoformat()
            }
            
            # Update working capital after the trade
            # For a buy order, we'll assume a small negative P&L for fees
            estimated_cost = final_quantity * current_price * 1.001  # Rough estimate for fees
            self.update_working_capital_after_trade(-estimated_cost)
            
            self.log_message(f"✅ Buy order successful! Order ID: {result.get('orderId')}")
            return trade
            
        except Exception as e:
            self.log_message(f"❌ Error executing buy order: {e}")
            return None
    
    def execute_sell(self, symbol, quantity=None):
        """Execute a sell order"""
        if symbol not in self.current_positions:
            self.log_message(f"❌ No position found for {symbol}")
            return None
        
        if quantity is None:
            quantity = self.current_positions[symbol]['quantity']
        
        try:
            # Get current price to calculate minimum order value
            current_price = self.get_current_price_from_api(symbol)
            if current_price <= 0:
                self.log_message(f"❌ Could not get current price for {symbol}")
                return None
            
            # Calculate minimum order value (typically $1 minimum on Bybit)
            min_order_value = 1.0
            min_quantity = min_order_value / current_price
            
            # Use 5% of working capital for position sizing
            working_capital = self.get_working_capital()
            position_value = working_capital * 0.05
            calculated_quantity = position_value / current_price
            
            # Use the larger of our calculated quantity or the minimum required
            final_quantity = max(calculated_quantity, min_quantity)
            
            # Create order data with properly formatted quantity
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": "Sell",
                "orderType": "Market",
                "qty": f"{final_quantity:.6f}",  # Format to 6 decimal places
                "timeInForce": "GTC"
            }
            
            self.log_message(f"📉 Placing SELL order for {final_quantity} {symbol}...")
            result, error = self.make_request("POST", "/v5/order/create", data=order_data)
            
            if error:
                self.log_message(f"❌ Sell order failed: {error}")
                return None
            
            # Record the trade
            trade = {
                'timestamp': datetime.now().isoformat(),
                'type': 'SELL',
                'symbol': symbol,
                'quantity': final_quantity,
                'order_id': result.get('orderId'),
                'status': result.get('orderStatus', 'Unknown')
            }
            
            self.trades.append(trade)
            del self.current_positions[symbol]
            
            # Update working capital after the trade
            # For a sell order, we'll assume a small positive P&L after fees
            estimated_revenue = final_quantity * current_price * 0.999  # Rough estimate after fees
            self.update_working_capital_after_trade(estimated_revenue)
            
            self.log_message(f"✅ Sell order successful! Order ID: {result.get('orderId')}")
            return trade
            
        except Exception as e:
            self.log_message(f"❌ Error executing sell order: {e}")
            return None
    
    def calculate_position_size(self, symbol):
        """Calculate position size based on working capital"""
        try:
            # Get current price
            current_price = self.get_current_price_from_api(symbol)
            if current_price <= 0:
                return 0.001  # Default fallback
            
            # Use 5% of WORKING capital for position sizing
            position_value = self.get_working_capital() * 0.05
            calculated_quantity = position_value / current_price
            
            # Log what we're doing
            self.log_message(f"📊 Position sizing: 5% of working capital = ${position_value:.2f}, calculated qty = {calculated_quantity:.6f}")
            
            return calculated_quantity
            
        except Exception as e:
            self.log_message(f"❌ Error calculating position size: {e}")
            return 0.001  # Default fallback
    
    def load_strategy(self):
        """Load the selected strategy with optimized parameters"""
        try:
            # First, check for optimized parameters
            from simple_strategy.trading.parameter_manager import ParameterManager
            pm = ParameterManager()
            optimized_params = pm.get_parameters(self.strategy_name)
            
            # Import the strategy registry to get available strategies
            from simple_strategy.strategies.strategy_registry import StrategyRegistry
            registry = StrategyRegistry()
            available_strategies = registry.get_all_strategies()
            
            # Check if the selected strategy exists
            if self.strategy_name not in available_strategies:
                self.log_message(f"Error: Unknown strategy '{self.strategy_name}'")
                self.log_message(f"Available strategies: {list(available_strategies.keys())}")
                return False
            
            # Get strategy info
            strategy_info = available_strategies[self.strategy_name]
            
            # Get default parameters from strategy info
            parameters_def = strategy_info.get('parameters', {})
            default_params = {}
            for param_name, param_info in parameters_def.items():
                default_params[param_name] = param_info.get('default', 0)
            
            # Use optimized parameters if available, otherwise use defaults
            current_params = optimized_params if optimized_params else default_params
            
            # Create the strategy using the create_func from the registry
            if 'create_func' in strategy_info:
                # Get symbols and timeframes - we'll use 1-minute data for paper trading
                symbols = ['BTCUSDT']  # We'll update this per symbol in generate_strategy_signal
                timeframes = ['1m']     # We're using 1-minute data
                
                # Create the strategy
                self.strategy = strategy_info['create_func'](
                    symbols=symbols,
                    timeframes=timeframes,
                    **current_params
                )
                
                self.log_message(f"Strategy '{self.strategy_name}' loaded successfully")
                if optimized_params:
                    self.log_message(f"Using optimized parameters (last optimized: {optimized_params.get('last_optimized', 'Unknown')})")
                else:
                    self.log_message("Using default parameters")
                return True
            else:
                self.log_message(f"Error: Strategy '{self.strategy_name}' missing create_func")
                return False
                    
        except Exception as e:
            self.log_message(f"Error loading strategy: {e}")
            import traceback
            self.log_message(f"Traceback: {traceback.format_exc()}")
            return False
    
    def generate_trading_signal(self, symbol, current_price):
        """Generate trading signal using the loaded strategy"""
        try:
            # First try to use the loaded strategy
            if self.strategy and hasattr(self.strategy, 'generate_signals'):
                return self.generate_strategy_signal(symbol)
            
            # Fallback to RSI strategy
            return self.generate_rsi_signal(symbol, current_price)
            
        except Exception as e:
            self.log_message(f"❌ Error generating signal for {symbol}: {e}")
            return 'HOLD'

    def generate_strategy_signal(self, symbol):
        """Generate signal using the loaded strategy"""
        try:
            # Get historical data for the symbol
            historical_data = self.get_historical_data_for_symbol(symbol)
            
            # Explicitly check for None or empty DataFrame
            if historical_data is None:
                self.log_message(f"⚠️ No historical data available for {symbol}")
                return 'HOLD'
            
            if isinstance(historical_data, pd.DataFrame) and historical_data.empty:
                self.log_message(f"⚠️ Empty historical data for {symbol}")
                return 'HOLD'
            
            if len(historical_data) < 50:
                self.log_message(f"⚠️ Not enough historical data for {symbol} (only {len(historical_data)} rows)")
                return 'HOLD'
            
            # Prepare data in the format expected by the strategy
            # The strategy expects: Dict[str, Dict[str, pd.DataFrame]]
            # where the first key is the symbol and the second key is the timeframe
            strategy_data = {
                symbol: {
                    "1m": historical_data  # We're using 1-minute data
                }
            }
            
            # Generate signals using the strategy
            try:
                signals = self.strategy.generate_signals(strategy_data)
                
                # Extract the signal for our symbol and timeframe
                if signals and symbol in signals and "1m" in signals[symbol]:
                    signal = signals[symbol]["1m"]
                    return signal
                else:
                    self.log_message(f"⚠️ No signal returned for {symbol}")
                    return 'HOLD'
                    
            except Exception as e:
                self.log_message(f"❌ Error generating signals: {e}")
                return 'HOLD'
            
        except Exception as e:
            self.log_message(f"❌ Error generating strategy signal for {symbol}: {e}")
            return 'HOLD'

    def generate_rsi_signal(self, symbol, current_price):
        """Generate trading signal using RSI strategy with optimized parameters"""
        try:
            # Get historical data for RSI calculation
            historical_data = self.get_historical_data_for_symbol(symbol)
            
            # Explicitly check for None or empty DataFrame
            if historical_data is None:
                self.log_message(f"⚠️ No historical data available for {symbol}")
                return 'HOLD'
            
            if isinstance(historical_data, pd.DataFrame) and historical_data.empty:
                self.log_message(f"⚠️ Empty historical data for {symbol}")
                return 'HOLD'
            
            if len(historical_data) < 50:
                self.log_message(f"⚠️ Not enough historical data for {symbol} (only {len(historical_data)} rows)")
                return 'HOLD'
            
            # Use your optimized parameters
            rsi_period = 33
            rsi_overbought = 80
            rsi_oversold = 24
            
            # Calculate RSI
            closes = historical_data['close'].values
            rsi_values = self.calculate_rsi(closes, period=rsi_period)
            
            if len(rsi_values) == 0:
                return 'HOLD'
            
            current_rsi = rsi_values[-1]
            
            # Generate signals based on your optimized RSI parameters
            if symbol not in self.current_positions:
                if current_rsi < rsi_oversold:  # Oversold - buy signal
                    self.log_message(f"📈 RSI BUY signal for {symbol}: RSI={current_rsi:.1f} < {rsi_oversold}")
                    return 'BUY'
            else:
                if current_rsi > rsi_overbought:  # Overbought - sell signal
                    self.log_message(f"📉 RSI SELL signal for {symbol}: RSI={current_rsi:.1f} > {rsi_overbought}")
                    return 'SELL'
            
            self.log_message(f"📊 RSI HOLD for {symbol}: RSI={current_rsi:.1f}")
            return 'HOLD'
            
        except Exception as e:
            self.log_message(f"❌ Error generating RSI signal for {symbol}: {e}")
            return 'HOLD'

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI properly"""
        try:
            if len(prices) < period + 1:
                return np.array([50.0] * len(prices))  # Default to neutral
            
            # Calculate price changes
            deltas = np.diff(prices)
            seed = deltas[:period+1]
            up = seed[seed >= 0].sum()/period
            down = -seed[seed < 0].sum()/period
            rs = up/down
            rsi = np.zeros_like(prices)
            rsi[:period] = 100. - (100./(1.+rs))
            
            # Calculate the rest of RSI values
            for i in range(period, len(prices)):
                delta = deltas[i-1]
                if delta > 0:
                    upval = delta
                    downval = 0.
                else:
                    upval = 0.
                    downval = -delta
                
                up = (up*(period-1) + upval)/period
                down = (down*(period-1) + downval)/period
                rs = up/down
                rsi[i] = 100. - (100./(1.+rs))
            
            return rsi
        except Exception as e:
            self.log_message(f"❌ Error calculating RSI: {e}")
            return np.array([50.0] * len(prices))  # Default to neutral

    def get_historical_data_for_symbol(self, symbol):
        """Get historical data for a symbol by loading directly from CSV."""
        return self.load_csv_data(symbol)

    def load_csv_data(self, symbol):
        """Load data directly from CSV file as fallback"""
        try:
            import pandas as pd
            
            # Construct the correct file path to the project's root 'data' folder
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            csv_file = os.path.join(project_root, 'data', f'{symbol}_1.csv')
            
            if not os.path.exists(csv_file):
                self.log_message(f"⚠️ CSV file not found for {symbol}: {csv_file}")
                return None
            
            # Load CSV file
            df = pd.read_csv(csv_file)
            
            # Ensure we have a DataFrame
            if not isinstance(df, pd.DataFrame):
                self.log_message(f"❌ Loaded data is not a DataFrame for {symbol}")
                return None
            
            # Check if DataFrame is empty
            if df.empty:
                self.log_message(f"⚠️ Empty DataFrame for {symbol}")
                return pd.DataFrame()  # Return empty DataFrame instead of None
            
            # Convert timestamp to datetime if needed
            if 'timestamp' in df.columns and 'datetime' not in df.columns:
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Sort by datetime
            df = df.sort_values('datetime')
            
            # Get last 1000 rows for RSI calculation
            if len(df) > 1000:
                df = df.tail(1000)
            
            self.log_message(f"✅ Loaded {len(df)} rows from CSV for {symbol}")
            return df
            
        except Exception as e:
            self.log_message(f"❌ Error loading CSV for {symbol}: {e}")
            return None
        
    def update_balance_after_trade(self, pnl_amount):
        """Update simulated balance after trade"""
        self.simulated_balance += pnl_amount
        self.log_message(f"💰 Balance updated: ${self.simulated_balance:.2f} (P&L: ${pnl_amount:.2f})")

    def get_balance_info(self):
        """Get complete balance information"""
        return {
            'simulated_balance': self.simulated_balance,
            'real_balance': self.real_balance,
            'balance_offset': self.balance_offset,
            'initial_balance': self.initial_balance,
            'total_pnl': self.simulated_balance - self.initial_balance
        }
    
    def start_trading(self):
        """Start paper trading with real API calls"""
        if not self.load_strategy():
            return False
        
        if not self.api_key or not self.api_secret:
            self.log_message("Error: API credentials not loaded")
            return False
        
        # Initialize shared data access
        self.initialize_shared_data_access()
        
        self.is_running = True
        self.log_message(f"Paper trading started for {self.strategy_name}")
        
        # --- NEW: Get symbols and intervals directly from our local data files ---
        symbols_to_monitor, available_intervals = self.get_symbols_and_intervals_from_data_dir()
        
        # For now, let's just use the 1-minute interval
        if '1' not in available_intervals:
            self.log_message("❌ No 1-minute interval data found. Cannot start.")
            return
            
        # You can limit the number of symbols for testing if you want
        # For example, to only test the first 50 symbols:
        # symbols_to_monitor = symbols_to_monitor[:50]
        self.log_message(f"📈 Monitoring {len(symbols_to_monitor)} symbols on the 1m interval.")
        
        # --- NEW: Main CSV-based trading loop ---
        loop_count = 0

        while self.is_running:
            loop_count += 1
            self.log_message(f"\n=== Trading Loop #{loop_count} ===")
            
            # Process each symbol by reading from the latest CSV data
            for symbol in symbols_to_monitor:
                try:
                    # Get the latest data for the symbol from the CSV file
                    historical_data = self.get_historical_data_for_symbol(symbol)
                    
                    if historical_data is not None and not historical_data.empty:
                        # Generate a trading signal based on this fresh data
                        signal = self.generate_trading_signal(symbol, historical_data.iloc[-1]['close'])
                        
                        if signal == 'BUY':
                            self.execute_buy(symbol)
                            # Add a small delay to avoid rate limiting
                            time.sleep(0.1)
                        elif signal == 'SELL':
                            self.execute_sell(symbol)
                            # Add a small delay to avoid rate limiting
                            time.sleep(0.1)
                        # No need to log 'HOLD' to keep the log cleaner

                except Exception as e:
                    self.log_message(f"❌ Error processing {symbol}: {e}")
                    continue
            
            # Update performance and wait for the next minute
            self.update_performance_display()
            if self.is_running:
                self.log_message("✅ Cycle complete. Waiting for the next minute...")
                time.sleep(60) # Wait 60 seconds before the next cycle

        self.log_message("🛑 Trading loop ended")
    
    def update_performance(self):
        """Update performance metrics with real data from Bybit"""
        try:
            # Get real balance from Bybit
            real_balance = self.get_balance()
            
            # Calculate P&L
            total_pnl = real_balance - self.initial_balance
            
            # Update performance metrics
            performance = {
                'real_balance': real_balance,
                'total_pnl': total_pnl,
                'total_trades': len(self.trades),
                'open_positions': len(self.current_positions)
            }
            
            self.log_message(f"Performance: Balance=${real_balance:.2f}, PNL=${total_pnl:.2f}")
            return performance
            
        except Exception as e:
            self.log_message(f"Error updating performance: {e}")
            return None

    def get_current_price_from_api(self, symbol):
        """Fallback method to get price from API"""
        try:
            result, error = self.make_request("GET", "/v5/market/tickers", 
                                            params={"category": "linear", "symbol": symbol})
            if result and 'list' in result and result['list']:
                return float(result['list'][0].get('lastPrice', 0))
            return 0
        except Exception as e:
            self.log_message(f"❌ Error getting price from API: {e}")
            return 0
        
    def get_performance_summary(self):
        """Get a summary of trading performance"""
        try:
            balance_info = self.get_balance_info()
            
            # Calculate win rate
            winning_trades = 0
            for trade in self.trades:
                # Simple check: if it's a sell trade and balance increased, count as win
                if trade['type'] == 'SELL' and trade.get('balance_after') and trade.get('balance_before'):
                    if trade['balance_after'] > trade['balance_before']:
                        winning_trades += 1
            
            total_sell_trades = sum(1 for trade in self.trades if trade['type'] == 'SELL')
            win_rate = (winning_trades / total_sell_trades * 100) if total_sell_trades > 0 else 0
            
            summary = {
                'initial_balance': balance_info['initial_balance'],
                'current_balance': balance_info['simulated_balance'],
                'total_pnl': balance_info['total_pnl'],
                'total_trades': len(self.trades),
                'win_rate': win_rate,
                'open_positions': len(self.current_positions),
                'status': 'Running' if self.is_running else 'Stopped'
            }
            
            return summary
        except Exception as e:
            self.log_message(f"Error generating performance summary: {e}")
            return {
                'error': str(e),
                'status': 'Error'
            }
        
    def stop_trading(self):
        """Stop paper trading"""
        self.is_running = False
        self.trading_loop_active = False
        self.log_message("🛑 Paper trading stopped by user")

    def process_symbol(self, symbol):
        """Process a single symbol for trading signals"""
        try:
            # Get current price
            current_price = self.get_current_price_from_api(symbol)
            if not current_price or current_price == 0:
                return
            
            self.log_message(f"💰 {symbol}: ${current_price}")
            
            # Get strategy signal
            signal = self.generate_trading_signal(symbol, current_price)
            
            if signal == 'BUY':
                self.execute_buy_signal(symbol, current_price)
            elif signal == 'SELL':
                self.execute_sell_signal(symbol, current_price)
            else:
                self.log_message(f"📊 Signal for {symbol}: HOLD")
                
        except Exception as e:
            self.log_message(f"❌ Error processing {symbol}: {e}")

    def update_performance_display(self):
        """Update performance display"""
        try:
            # Get working capital
            working_capital = self.get_working_capital()
            
            # Calculate total P&L
            initial_capital = self.initial_balance
            total_pnl = working_capital - initial_capital
            
            # Calculate win rate
            winning_trades = 0
            total_sell_trades = 0
            
            for trade in self.trades:
                if trade['type'] == 'SELL':
                    total_sell_trades += 1
                    if 'pnl' in trade and trade['pnl'] > 0:
                        winning_trades += 1
            
            win_rate = (winning_trades / total_sell_trades * 100) if total_sell_trades > 0 else 0
            
            # Log performance
            self.log_message(f"Performance: Working Capital=${working_capital:.2f}, PNL=${total_pnl:.2f}")
            self.log_message(f"Open positions: {len(self.current_positions)}")
            self.log_message(f"Total trades: {len(self.trades)}")
            
            # Update GUI if available
            if self.performance_callback:
                performance_data = {
                    'balance': working_capital,  # Use working capital
                    'pnl': total_pnl,
                    'win_rate': win_rate,
                    'open_positions': len(self.current_positions),
                    'total_trades': len(self.trades)
                }
                self.performance_callback(performance_data)
                
        except Exception as e:
            self.log_message(f"❌ Error updating performance: {e}")

    def get_symbols_and_intervals_from_data_dir(self):
        """
        Scans the data directory to find all available symbols and intervals.
        This is a fast, reliable way to know what data we have locally.
        """
        start_time = time.time()
        
        # Get the absolute path to the project's root 'data' folder
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, 'data')

        symbols = set()
        intervals = set()
        file_count = 0

        self.log_message(f"🔍 Scanning for symbols in {data_dir}...")

        try:
            for filename in os.listdir(data_dir):
                if filename.endswith('.csv'):
                    # Expected format: SYMBOL_INTERVAL.csv (e.g., BTCUSDT_1.csv)
                    parts = filename[:-4].split('_') # Remove .csv and split by _
                    if len(parts) == 2:
                        symbol = parts[0]
                        interval = parts[1]
                        symbols.add(symbol)
                        intervals.add(interval)
                        file_count += 1
        except FileNotFoundError:
            self.log_message(f"❌ Error: Data directory not found at {data_dir}")
            return [], []

        end_time = time.time()
        duration = end_time - start_time

        # Log the statistics
        self.log_message(f"✅ Scan complete in {duration:.2f} seconds.")
        self.log_message(f"📊 Found {file_count} data files.")
        self.log_message(f"📈 Found {len(symbols)} unique symbols: {', '.join(list(symbols)[:10])}...")
        self.log_message(f"⏱️ Found {len(intervals)} unique intervals: {', '.join(sorted(list(intervals)))}")

        return sorted(list(symbols)), sorted(list(intervals))