import os
import json
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode
from datetime import datetime
from simple_strategy.shared.data_feeder import DataFeeder

class PaperTradingEngine:
    def __init__(self, api_account, strategy_name, simulated_balance=1000):
        self.api_account = api_account
        self.strategy_name = strategy_name
        self.simulated_balance = float(simulated_balance)
        self.initial_balance = self.simulated_balance
        
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
        
        # Data feeder for strategy integration
        self.data_feeder = DataFeeder(data_dir='data')
        
        print(f"Paper Trading Engine initialized:")
        print(f" Account: {api_account}")
        print(f" Strategy: {strategy_name}")
        print(f" Simulated Balance: ${simulated_balance}")
        
        # Load credentials and test connection
        self.load_credentials()
        self.test_connection()
    
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
                    print(f"✅ API credentials loaded for {self.api_account}")
                    return True
            
            print(f"❌ Account '{self.api_account}' not found")
            return False
            
        except Exception as e:
            print(f"❌ Error loading API credentials: {e}")
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
    
    def test_connection(self):
        """Test the connection - EXACT working method"""
        try:
            print("Testing connection...")
            result, error = self.make_request("GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"})
            
            if error:
                print(f"❌ Connection test failed: {error}")
                return False
            
            if result and 'list' in result and result['list']:
                wallet_data = result['list'][0]
                balance = float(wallet_data.get('totalAvailableBalance', '0'))
                print(f"✅ Connection successful! Balance: ${balance}")
                return True
            else:
                print("❌ Connection test failed: Invalid response format")
                return False
                
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False
    
    def get_balance(self):
        """Get current balance"""
        try:
            result, error = self.make_request("GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"})
            
            if error:
                print(f"❌ Error getting balance: {error}")
                return 0
            
            if result and 'list' in result and result['list']:
                wallet_data = result['list'][0]
                balance = float(wallet_data.get('totalAvailableBalance', '0'))
                return balance
            else:
                return 0
                
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return 0
    
    def get_all_perpetual_symbols(self):
        """Get all perpetual symbols"""
        try:
            result, error = self.make_request("GET", "/v5/market/instruments-info", params={"category": "linear", "limit": 1000})
            
            if error:
                print(f"❌ Error getting symbols: {error}")
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
            
            print(f"✅ Found {len(symbols)} perpetual symbols")
            return sorted(symbols)
                
        except Exception as e:
            print(f"❌ Error getting symbols: {e}")
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
            
            print(f"📈 Placing BUY order for {quantity} {symbol}...")
            result, error = self.make_request("POST", "/v5/order/create", data=order_data)
            
            if error:
                print(f"❌ Buy order failed: {error}")
                return None
            
            # Record the trade
            trade = {
                'timestamp': datetime.now().isoformat(),
                'type': 'BUY',
                'symbol': symbol,
                'quantity': quantity,
                'order_id': result.get('orderId'),
                'status': result.get('orderStatus', 'Unknown'),
                'balance_before': self.get_balance(),
                'balance_after': None
            }
            
            self.trades.append(trade)
            self.current_positions[symbol] = {
                'quantity': quantity,
                'order_id': result.get('orderId'),
                'entry_time': datetime.now().isoformat()
            }
            
            print(f"✅ Buy order successful! Order ID: {result.get('orderId')}")
            return trade
            
        except Exception as e:
            print(f"❌ Error executing buy order: {e}")
            return None
    
    def execute_sell(self, symbol, quantity=None):
        """Execute a sell order"""
        if symbol not in self.current_positions:
            print(f"❌ No position found for {symbol}")
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
            
            print(f"📉 Placing SELL order for {quantity} {symbol}...")
            result, error = self.make_request("POST", "/v5/order/create", data=order_data)
            
            if error:
                print(f"❌ Sell order failed: {error}")
                return None
            
            # Record the trade
            trade = {
                'timestamp': datetime.now().isoformat(),
                'type': 'SELL',
                'symbol': symbol,
                'quantity': quantity,
                'order_id': result.get('orderId'),
                'status': result.get('orderStatus', 'Unknown'),
                'balance_before': self.get_balance(),
                'balance_after': None
            }
            
            self.trades.append(trade)
            del self.current_positions[symbol]
            
            print(f"✅ Sell order successful! Order ID: {result.get('orderId')}")
            return trade
            
        except Exception as e:
            print(f"❌ Error executing sell order: {e}")
            return None
    
    def calculate_position_size(self, symbol):
        """Calculate position size based on available balance"""
        # Simple position sizing - use 1% of simulated balance
        position_value = self.simulated_balance * 0.01
        return 0.001  # Fixed small size for testing
    
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
                    print(f"Strategy '{self.strategy_name}' loaded with optimized parameters")
                    print(f"Last optimized: {optimized_params.get('last_optimized', 'Unknown')}")
                else:
                    # Use default parameters
                    self.strategy = strategy_module.create_strategy()
                    print(f"Strategy '{self.strategy_name}' loaded with default parameters")
                    print("⚠️ Warning: No optimized parameters found")
                return True
            else:
                print(f"Error: Strategy '{self.strategy_name}' missing create_strategy function")
                return False
                
        except Exception as e:
            print(f"Error loading strategy: {e}")
            return False
    
    def generate_trading_signal(self, symbol, current_price):
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
            print(f"Error generating signal for {symbol}: {e}")
            return None
    
    def start_trading(self):
        """Start paper trading with real API calls"""
        if not self.load_strategy():
            return False
        
        if not self.api_key or not self.api_secret:
            print("Error: API credentials not loaded")
            return False
        
        self.is_running = True
        print(f"Paper trading started for {self.strategy_name}")
        
        # Get all perpetual symbols
        symbols = self.get_all_perpetual_symbols()
        print(f"Monitoring {len(symbols)} symbols")
        
        # For testing, start with a smaller subset
        test_symbols = symbols[:10]  # Start with 10 symbols for testing
        print(f"Testing with first {len(test_symbols)} symbols: {test_symbols}")
        
        # Main trading loop
        loop_count = 0
        while self.is_running:
            loop_count += 1
            print(f"\n=== Trading Loop #{loop_count} ===")
            
            try:
                # Get real-time data for all test symbols
                for symbol in test_symbols:
                    try:
                        # Fetch latest ticker data
                        result, error = self.make_request("GET", "/v5/market/tickers", params={"category": "linear", "symbol": symbol})
                        
                        if error:
                            print(f"Error fetching ticker for {symbol}: {error}")
                            continue
                        
                        # Extract current price from result
                        ticker_data = result['list'][0] if result['list'] else None
                        if not ticker_data:
                            continue
                        
                        current_price = float(ticker_data.get('lastPrice', 0))
                        if current_price == 0:
                            continue
                        
                        print(f"{symbol}: ${current_price}")
                        
                        # Generate trading signal using your strategy
                        signal = self.generate_trading_signal(symbol, current_price)
                        
                        # Execute trade if signal is strong enough
                        if signal == 'BUY' and symbol not in self.current_positions:
                            print(f"📈 BUY signal for {symbol} at ${current_price}")
                            self.execute_buy(symbol)
                        elif signal == 'SELL' and symbol in self.current_positions:
                            print(f"📉 SELL signal for {symbol} at ${current_price}")
                            self.execute_sell(symbol)
                        elif signal:
                            print(f"📊 Signal for {symbol}: {signal}")
                        
                    except Exception as e:
                        print(f"Error processing {symbol}: {e}")
                        continue
                
                # Update balance and performance
                self.update_performance()
                
                # Print current status
                print(f"Open positions: {len(self.current_positions)}")
                print(f"Total trades: {len(self.trades)}")
                
                # Check if we should stop (for testing)
                if loop_count >= 3:  # Stop after 3 loops for testing
                    print("🛑 Stopping after 3 test loops")
                    self.is_running = False
                    break
                
                # Sleep to avoid rate limits
                print("⏳ Waiting 30 seconds before next loop...")
                time.sleep(30)
                
            except Exception as e:
                print(f"Error in trading loop: {e}")
                time.sleep(5)
        
        print("Paper trading stopped")
        print(f"Final stats:")
        print(f"  Total loops: {loop_count}")
        print(f"  Total trades: {len(self.trades)}")
        print(f"  Open positions: {len(self.current_positions)}")
    
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
            
            print(f"Performance: Balance=${real_balance:.2f}, PNL=${total_pnl:.2f}")
            return performance
            
        except Exception as e:
            print(f"Error updating performance: {e}")
            return None