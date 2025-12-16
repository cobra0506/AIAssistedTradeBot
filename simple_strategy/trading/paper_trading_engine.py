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
    def __init__(self, api_account, strategy_name, simulated_balance=1000, log_callback=None, status_callback=None, performance_callback=None):
        self.api_account = api_account
        self.strategy_name = strategy_name
        self.simulated_balance = float(simulated_balance)
        self.initial_balance = self.simulated_balance
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
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        self.log_message(f"  Simulated Balance: ${simulated_balance}")
        
        # Load credentials and test connection
        self.load_credentials()
        self.test_connection()
        
        # Get real balance and calculate offset
        self.real_balance = self.get_real_balance()
        self.balance_offset = self.real_balance - self.simulated_balance
        self.log_message(f"  Real Balance: ${self.real_balance}")
        self.log_message(f"  Balance Offset: ${self.balance_offset}")

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
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": "Buy",
                "orderType": "Market",
                "qty": str(quantity),
                "timeInForce": "GTC"
            }
            
            self.log_message(f"📈 Placing BUY order for {quantity} {symbol}...")
            result, error = self.make_request("POST", "/v5/order/create", data=order_data)
            
            if error:
                self.log_message(f"❌ Buy order failed: {error}")
                return None
            
            # Record the trade
            balance_before = self.get_display_balance()
            trade = {
                'timestamp': datetime.now().isoformat(),
                'type': 'BUY',
                'symbol': symbol,
                'quantity': quantity,
                'order_id': result.get('orderId'),
                'status': result.get('orderStatus', 'Unknown'),
                'balance_before': balance_before,
                'balance_after': None
            }
            
            self.trades.append(trade)
            self.current_positions[symbol] = {
                'quantity': quantity,
                'order_id': result.get('orderId'),
                'entry_time': datetime.now().isoformat()
            }
            
            self.log_message(f"✅ Buy order successful! Order ID: {result.get('orderId')}")
            # Update balance (simple simulation - deduct estimated cost)
            estimated_cost = quantity * 50000  # Simple estimate for testing
            self.update_balance_after_trade(-estimated_cost)
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
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": "Sell",
                "orderType": "Market",
                "qty": str(quantity),
                "timeInForce": "GTC"
            }
            
            self.log_message(f"📉 Placing SELL order for {quantity} {symbol}...")
            result, error = self.make_request("POST", "/v5/order/create", data=order_data)
            
            if error:
                self.log_message(f"❌ Sell order failed: {error}")
                return None
            
            # Record the trade
            balance_before = self.get_display_balance()
            trade = {
                'timestamp': datetime.now().isoformat(),
                'type': 'SELL',
                'symbol': symbol,
                'quantity': quantity,
                'order_id': result.get('orderId'),
                'status': result.get('orderStatus', 'Unknown'),
                'balance_before': balance_before,
                'balance_after': None
            }
            
            self.trades.append(trade)
            del self.current_positions[symbol]
            
            self.log_message(f"✅ Sell order successful! Order ID: {result.get('orderId')}")
            # Update balance (simple simulation - add estimated revenue)
            estimated_revenue = quantity * 55000  # Simple estimate for testing
            self.update_balance_after_trade(estimated_revenue)
            return trade
            
        except Exception as e:
            self.log_message(f"❌ Error executing sell order: {e}")
            return None
    
    def calculate_position_size(self, symbol):
        """Calculate position size based on available simulated balance"""
        # Use 1% of simulated balance for position sizing
        position_value = self.get_display_balance() * 0.01
        # Return a reasonable position size (0.001 is good for testing)
        return 0.001
    
    def load_strategy(self):
        """Load the selected strategy with optimized parameters"""
        try:
            # First, check for optimized parameters
            from simple_strategy.trading.parameter_manager import ParameterManager
            pm = ParameterManager()
            optimized_params = pm.get_parameters(self.strategy_name)
            
            # Import the strategy file
            strategy_module = __import__(f'simple_strategy.strategies.{self.strategy_name}', fromlist=[''])
            
            # Get the strategy function
            if hasattr(strategy_module, 'create_strategy'):
                if optimized_params:
                    # Use optimized parameters
                    self.strategy = strategy_module.create_strategy(**optimized_params)
                    self.log_message(f"Strategy '{self.strategy_name}' loaded with optimized parameters")
                    self.log_message(f"Last optimized: {optimized_params.get('last_optimized', 'Unknown')}")
                else:
                    # Use default parameters
                    self.strategy = strategy_module.create_strategy()
                    self.log_message(f"Strategy '{self.strategy_name}' loaded with default parameters")
                    self.log_message("⚠️ Warning: No optimized parameters found")
                return True
            else:
                self.log_message(f"Error: Strategy '{self.strategy_name}' missing create_strategy function")
                return False
                
        except Exception as e:
            self.log_message(f"Error loading strategy: {e}")
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
            
            if not historical_data or len(historical_data) < 50:
                self.log_message(f"⚠️ Not enough historical data for {symbol}")
                return 'HOLD'
            
            # Generate signals using the strategy
            signals = self.strategy.generate_signals(historical_data)
            
            # Get the latest signal
            if signals is not None and len(signals) > 0:
                if isinstance(signals, pd.DataFrame):
                    latest_signal = signals.iloc[-1]['signal']
                elif isinstance(signals, dict) and 'signal' in signals:
                    latest_signal = signals['signal']
                else:
                    latest_signal = signals[-1] if isinstance(signals, (list, np.ndarray)) else 0
                
                # Convert signal to string
                if latest_signal == 1:
                    return 'BUY'
                elif latest_signal == -1:
                    return 'SELL'
                else:
                    return 'HOLD'
            
            return 'HOLD'
            
        except Exception as e:
            self.log_message(f"❌ Error generating strategy signal for {symbol}: {e}")
            return 'HOLD'

    def generate_rsi_signal(self, symbol, current_price):
        """Generate trading signal using RSI strategy with optimized parameters"""
        try:
            # Get historical data for RSI calculation
            historical_data = self.get_historical_data_for_symbol(symbol)
            
            if not historical_data or len(historical_data) < 50:
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
        """Get historical data for a symbol"""
        try:
            # Calculate date range (last 7 days for RSI calculation)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # Format dates for data feeder
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # Try to get data from data feeder with required parameters
            data = self.data_feeder.get_data_for_symbols(
                symbols=[symbol], 
                timeframes=['5m'],
                start_date=start_date_str,
                end_date=end_date_str
            )
            
            if data and symbol in data:
                return data[symbol]
            
            # Fallback: try to load CSV file directly
            return self.load_csv_data(symbol)
            
        except Exception as e:
            self.log_message(f"❌ Error getting historical data for {symbol}: {e}")
            return None

    def load_csv_data(self, symbol):
        """Load data directly from CSV file as fallback"""
        try:
            import pandas as pd
            
            # Construct the correct file path to the project's root 'data' folder
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_file = os.path.join(project_root, 'data', f'{symbol}_1.csv')
            
            if not os.path.exists(csv_file):
                self.log_message(f"⚠️ CSV file not found for {symbol}: {csv_file}")
                return None
            
            # Load CSV file
            df = pd.read_csv(csv_file)
            
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
        
        # Get all perpetual symbols
        all_symbols = self.get_all_perpetual_symbols()
        
        # Filter to only tradable symbols
        tradable_symbols = self.filter_tradable_symbols(all_symbols)
        
        # Limit to first 50 for performance
        symbols_to_monitor = tradable_symbols[:50]
        self.log_message(f"📈 Monitoring {len(symbols_to_monitor)} symbols")
        
        # Main trading loop
        loop_count = 0
        max_loops = 1000  # Run indefinitely until stopped
        
        while self.is_running and loop_count < max_loops:
            loop_count += 1
            self.log_message(f"\n=== Trading Loop #{loop_count} ===")
            
            # Process each symbol
            for symbol in symbols_to_monitor:
                try:
                    self.process_symbol(symbol)
                except Exception as e:
                    self.log_message(f"❌ Error processing {symbol}: {e}")
                    continue
            
            # Update performance
            self.update_performance_display()
            
            # Wait before next loop
            if self.is_running:
                self.log_message("⏳ Waiting 30 seconds before next loop...")
                time.sleep(30)
        
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

    def execute_buy_signal(self, symbol, current_price):
        """Execute a buy signal if conditions are met"""
        # Check if we already have a position in this symbol
        if symbol in self.current_positions:
            self.log_message(f"⚠️ Already have position in {symbol}, skipping buy")
            return
        
        # Check max positions limit
        if len(self.current_positions) >= 3:  # Your max positions
            self.log_message(f"⚠️ Max positions reached, skipping buy for {symbol}")
            return
        
        # Calculate position size (2% risk per trade)
        position_size = self.simulated_balance * 0.02
        quantity = position_size / current_price
        
        # Execute the trade
        self.log_message(f"🚀 BUY {symbol}: {quantity:.6f} units at ${current_price}")
        
        # Record the position
        self.current_positions[symbol] = {
            'quantity': quantity,
            'entry_price': current_price,
            'timestamp': datetime.now()
        }
        
        # Update balance
        self.simulated_balance -= position_size
        
        # Record the trade
        self.trades.append({
            'symbol': symbol,
            'type': 'BUY',
            'quantity': quantity,
            'price': current_price,
            'timestamp': datetime.now()
        })

    def execute_sell_signal(self, symbol, current_price):
        """Execute a sell signal if we have a position"""
        if symbol not in self.current_positions:
            self.log_message(f"⚠️ No position in {symbol}, skipping sell")
            return
        
        position = self.current_positions[symbol]
        quantity = position['quantity']
        entry_price = position['entry_price']
        
        # Calculate P&L
        pnl = (current_price - entry_price) * quantity
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
        
        # Execute the sell
        self.log_message(f"💰 SELL {symbol}: {quantity:.6f} units at ${current_price} (P&L: ${pnl:.2f}, {pnl_percent:+.2f}%)")
        
        # Remove position
        del self.current_positions[symbol]
        
        # Update balance
        self.simulated_balance += quantity * current_price
        
        # Record the trade
        self.trades.append({
            'symbol': symbol,
            'type': 'SELL',
            'quantity': quantity,
            'price': current_price,
            'pnl': pnl,
            'timestamp': datetime.now()
        })

    def update_performance_display(self):
        """Update performance display"""
        try:
            # Calculate total P&L
            total_pnl = self.simulated_balance - self.initial_balance
            
            # Calculate win rate
            winning_trades = 0
            total_sell_trades = 0
            
            for trade in self.trades:
                if trade['type'] == 'SELL' and 'pnl' in trade:
                    total_sell_trades += 1
                    if trade['pnl'] > 0:
                        winning_trades += 1
            
            win_rate = (winning_trades / total_sell_trades * 100) if total_sell_trades > 0 else 0
            
            # Log performance
            self.log_message(f"Performance: Balance=${self.simulated_balance:.2f}, PNL=${total_pnl:.2f}")
            self.log_message(f"Open positions: {len(self.current_positions)}")
            self.log_message(f"Total trades: {len(self.trades)}")
            
            # Update GUI if available
            if self.performance_callback:
                performance_data = {
                    'balance': self.simulated_balance,
                    'pnl': total_pnl,
                    'win_rate': win_rate,
                    'open_positions': len(self.current_positions),
                    'total_trades': len(self.trades)
                }
                self.performance_callback(performance_data)
                
        except Exception as e:
            self.log_message(f"❌ Error updating performance: {e}")