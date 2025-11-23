import os
import json
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from datetime import datetime
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
        self.data_feeder = DataFeeder(data_dir='data')
        
        # GUI callback functions
        self.log_callback = log_callback
        self.status_callback = status_callback
        self.performance_callback = performance_callback
        
        # NEW: Use shared data access instead of creating new data collection
        # Initialize this later to avoid recursion issues
        self.shared_data_access = None
        
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
        self.log_message(message)  # Keep console logging for debugging
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
        
    def get_performance_summary(self):
        """Get a summary of trading performance"""
        try:
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
                'initial_balance': self.initial_balance,
                'current_balance': self.simulated_balance,
                'total_pnl': self.simulated_balance - self.initial_balance,
                'trades': self.trades,
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
                'status': 'Error',
                'initial_balance': self.initial_balance,
                'current_balance': self.simulated_balance,
                'total_pnl': 0,
                'trades': [],
                'total_trades': 0,
                'win_rate': 0,
                'open_positions': 0
            }
    
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
    
    def generate_trading_signal(self, symbol, current_price=None):
        """Generate trading signal using data from collection system"""
        # Get current price from data system if not provided
        if current_price is None:
            current_price = self.get_current_price_from_data_system(symbol)
            self.log_message(f"💰 Current price for {symbol}: ${current_price}")
        """Generate trading signal - simple test strategy"""
        try:
            # Simple test strategy: 
            # - Buy if price is below $50,000 (for BTC-like symbols)
            # - Sell if we have a position and price is above $60,000
            # - For other symbols, use scaled thresholds
            
            # Determine price threshold based on symbol
            if symbol == 'BTCUSDT':
                buy_threshold = 50000
                sell_threshold = 60000
            elif symbol == 'ETHUSDT':
                buy_threshold = 3000
                sell_threshold = 3500
            else:
                # For other symbols, use a simple percentage-based approach
                buy_threshold = current_price * 0.99  # Buy if 1% below current
                sell_threshold = current_price * 1.01  # Sell if 1% above current
            
            # Generate signals
            if symbol not in self.current_positions:
                if current_price < buy_threshold:
                    return 'BUY'
            else:
                if current_price > sell_threshold:
                    return 'SELL'
            
            return 'HOLD'  # Hold current position
            
        except Exception as e:
            self.log_message(f"Error generating signal for {symbol}: {e}")
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
        
        self.is_running = True
        self.log_message(f"Paper trading started for {self.strategy_name}")
        
        # Get all perpetual symbols
        symbols = self.get_all_perpetual_symbols()
        self.log_message(f"Monitoring {len(symbols)} symbols")
        
        # For testing, start with a smaller subset
        test_symbols = symbols[:10]  # Start with 10 symbols for testing
        self.log_message(f"Testing with first {len(test_symbols)} symbols: {test_symbols}")
        
        # Main trading loop
        loop_count = 0
        while self.is_running:
            loop_count += 1
            self.log_message(f"\n=== Trading Loop #{loop_count} ===")
            
            try:
                # Get real-time data for all test symbols
                for symbol in test_symbols:
                    try:
                        # Fetch latest ticker data
                        result, error = self.make_request("GET", "/v5/market/tickers", params={"category": "linear", "symbol": symbol})
                        
                        if error:
                            self.log_message(f"Error fetching ticker for {symbol}: {error}")
                            continue
                        
                        # Extract current price from result
                        ticker_data = result['list'][0] if result['list'] else None
                        if not ticker_data:
                            continue
                        
                        current_price = float(ticker_data.get('lastPrice', 0))
                        if current_price == 0:
                            continue
                        
                        self.log_message(f"{symbol}: ${current_price}")
                        
                        # Generate trading signal (let data system get the price)
                        signal = self.generate_trading_signal(symbol)  # Don't pass current_price
                        
                        # Execute trade if signal is strong enough
                        if signal == 'BUY' and symbol not in self.current_positions:
                            self.log_message(f"📈 BUY signal for {symbol} at ${current_price}")
                            self.execute_buy(symbol)
                        elif signal == 'SELL' and symbol in self.current_positions:
                            self.log_message(f"📉 SELL signal for {symbol} at ${current_price}")
                            self.execute_sell(symbol)
                        elif signal:
                            self.log_message(f"📊 Signal for {symbol}: {signal}")
                        
                    except Exception as e:
                        self.log_message(f"Error processing {symbol}: {e}")
                        continue
                
                # Update balance and performance
                self.update_performance()
                
                # self.log_message current status
                self.log_message(f"Open positions: {len(self.current_positions)}")
                self.log_message(f"Total trades: {len(self.trades)}")
                
                # Check if we should stop (for testing)
                if loop_count >= 3:  # Stop after 3 loops for testing
                    self.log_message("🛑 Stopping after 3 test loops")
                    self.is_running = False
                    break
                
                # Sleep to avoid rate limits
                self.log_message("⏳ Waiting 30 seconds before next loop...")
                time.sleep(30)
                
            except Exception as e:
                self.log_message(f"Error in trading loop: {e}")
                time.sleep(5)
        
        self.log_message("Paper trading stopped")
        self.log_message(f"Final stats:")
        self.log_message(f"  Total loops: {loop_count}")
        self.log_message(f"  Total trades: {len(self.trades)}")
        self.log_message(f"  Open positions: {len(self.current_positions)}")
    
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
        
    def initialize_data_system(self):
        """Initialize the data collection system"""
        try:
            self.log_message("📊 Initializing data collection system...")
            # Create a simple event loop for initialization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Initialize shared WebSocket if not already initialized
            if not self.shared_ws_manager.get_websocket_handler():
                loop.run_until_complete(self.shared_ws_manager.initialize(self.data_config))
            
            # Get the shared WebSocket handler
            self.data_system.websocket_handler = self.shared_ws_manager.get_websocket_handler()
            
            # Initialize the data system
            loop.run_until_complete(self.data_system.initialize())
            
            # Start data collection - get BOTH historical and real-time
            if self.data_config.FETCH_ALL_SYMBOLS:
                self.log_message(f"📊 Collecting data for ALL available symbols...")
            else:
                self.log_message(f"📊 Collecting data for {len(self.symbols_to_collect)} symbols...")
                
            loop.run_until_complete(self.data_system.fetch_data_hybrid(
                symbols=self.symbols_to_collect,  # None if FETCH_ALL_SYMBOLS is True
                mode="full"  # Get both historical and real-time data
            ))
            
            self.data_system_initialized = True
            self.log_message("✅ Data collection system initialized with shared WebSocket!")
            loop.close()
            
        except Exception as e:
            self.log_message(f"❌ Error initializing data system: {e}")
            #self.data_system_initialized = False

    def get_current_price_from_data_system(self, symbol):
        """Get current price from data collection system"""
        if not self.data_system_initialized:
            self.log_message("⚠️ Data system not initialized, using API fallback")
            return self.get_current_price_from_api(symbol)
        
        try:
            # Get the latest data from WebSocket (real-time)
            data = self.data_system.get_data(symbol, "1", source="websocket")
            
            if data and len(data) > 0:
                # Get the most recent candle's close price
                latest_candle = data[-1]
                return float(latest_candle['close'])
            else:
                # Fallback to memory data if no real-time data
                data = self.data_system.get_data(symbol, "1", source="memory")
                if data and len(data) > 0:
                    latest_candle = data[-1]
                    return float(latest_candle['close'])
                else:
                    self.log_message(f"⚠️ No data found for {symbol}, using API fallback")
                    return self.get_current_price_from_api(symbol)
                    
        except Exception as e:
            self.log_message(f"❌ Error getting price from data system: {e}")
            return self.get_current_price_from_api(symbol)

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