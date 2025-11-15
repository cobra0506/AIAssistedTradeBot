import os
import json
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode

class SimpleWorkingEngine:
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
        
        print(f"Simple Working Engine initialized:")
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
    
    def get_symbols(self):
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
            
            print(f"✅ Found {len(symbols)} symbols")
            return sorted(symbols)
                
        except Exception as e:
            print(f"❌ Error getting symbols: {e}")
            return []
    
    def execute_buy(self, symbol, quantity=0.001):
        """Execute a buy order - EXACT working method"""
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
            
            print(f"✅ Buy order successful! Order ID: {result.get('orderId')}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing buy order: {e}")
            return None
    
    def execute_sell(self, symbol, quantity=0.001):
        """Execute a sell order - EXACT working method"""
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
            
            print(f"✅ Sell order successful! Order ID: {result.get('orderId')}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing sell order: {e}")
            return None