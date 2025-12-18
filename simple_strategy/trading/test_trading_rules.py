import os
import json
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode

class BybitTradingRules:
    def __init__(self):
        # API configuration
        self.api_key = None
        self.api_secret = None
        self.base_url = "https://api-demo.bybit.com"
        self.recv_window = "5000"
        
        # Cache for symbol information
        self.symbol_info_cache = {}
        
        # Load credentials
        self.load_credentials()
    
    def load_credentials(self):
        """Load API credentials from file"""
        try:
            # Correct path to api_accounts.json
            current_dir = os.path.dirname(os.path.abspath(__file__))
            api_accounts_file = os.path.join(current_dir, 'api_accounts.json')
            
            with open(api_accounts_file, 'r') as f:
                accounts = json.load(f)
            
            # Find the demo account
            if 'bybit_demo' in accounts.get('demo_accounts', {}):
                account_info = accounts['demo_accounts']['bybit_demo']
                self.api_key = account_info['api_key']
                self.api_secret = account_info['api_secret']
                print("✅ API credentials loaded for bybit_demo")
                return True
            
            print("❌ Account 'bybit_demo' not found")
            return False
            
        except Exception as e:
            print(f"❌ Error loading API credentials: {e}")
            return False
    
    def generate_signature(self, timestamp, method, path, body='', params=None):
        """Generate HMAC-SHA256 signature"""
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
        """Make authenticated request"""
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
    
    def get_all_symbols_info(self):
        """Get information for all symbols at once and cache it"""
        try:
            result, error = self.make_request("GET", "/v5/market/instruments-info", 
                                            params={"category": "linear", "limit": 1000})
            
            if error:
                print(f"❌ Error getting symbols info: {error}")
                return False
            
            if result and 'list' in result and result['list']:
                # Cache all symbol information
                for symbol_info in result['list']:
                    symbol = symbol_info.get('symbol', '')
                    if symbol:
                        self.symbol_info_cache[symbol] = symbol_info
                
                print(f"✅ Cached information for {len(self.symbol_info_cache)} symbols")
                return True
            else:
                print("❌ No symbol information found")
                return False
                
        except Exception as e:
            print(f"❌ Error getting symbols info: {e}")
            return False
    
    def get_symbol_info(self, symbol):
        """Get detailed information about a specific symbol from cache"""
        if symbol in self.symbol_info_cache:
            return self.symbol_info_cache[symbol]
        return None
    
    def format_trading_rules(self, symbol_info):
        """Format trading rules for display"""
        if not symbol_info:
            return None
        
        try:
            symbol = symbol_info.get('symbol', 'Unknown')
            
            # Extract trading rules from lotSizeFilter
            lot_size_filter = symbol_info.get('lotSizeFilter', {})
            price_filter = symbol_info.get('priceFilter', {})
            
            rules = {
                'symbol': symbol,
                'status': symbol_info.get('status', 'Unknown'),
                'base_coin': symbol_info.get('baseCoin', 'Unknown'),
                'quote_coin': symbol_info.get('quoteCoin', 'Unknown'),
                'min_order_qty': float(lot_size_filter.get('minOrderQty', '0')),
                'max_order_qty': float(lot_size_filter.get('maxOrderQty', '0')),
                'qty_step': float(lot_size_filter.get('qtyStep', '0')),
                'min_notional_value': float(lot_size_filter.get('minNotionalValue', '0')),
                'max_mkt_order_qty': float(lot_size_filter.get('maxMktOrderQty', '0')),
                'min_price': float(price_filter.get('minPrice', '0')),
                'max_price': float(price_filter.get('maxPrice', '0')),
                'price_tick': float(price_filter.get('tickSize', '0')),
                'leverage_filter': symbol_info.get('leverageFilter', {})
            }
            
            return rules
        except Exception as e:
            print(f"❌ Error formatting trading rules: {e}")
            return None
    
    def display_trading_rules(self, symbols):
        """Display trading rules for multiple symbols"""
        print("\n" + "="*80)
        print("BYBIT TRADING RULES")
        print("="*80)
        
        for symbol in symbols:
            symbol_info = self.get_symbol_info(symbol)
            rules = self.format_trading_rules(symbol_info)
            
            if rules:  # Check if rules is not None
                print(f"\n📊 Symbol: {rules['symbol']}")
                print(f"   Status: {rules['status']}")
                print(f"   Base/Quote: {rules['base_coin']}/{rules['quote_coin']}")
                print(f"   Quantity Range: {rules['min_order_qty']} - {rules['max_order_qty']}")
                print(f"   Quantity Step: {rules['qty_step']}")
                print(f"   Min Notional Value: ${rules['min_notional_value']}")
                print(f"   Max Market Order Qty: {rules['max_mkt_order_qty']}")
                print(f"   Price Range: ${rules['min_price']} - ${rules['max_price']}")
                print(f"   Price Tick: ${rules['price_tick']}")
                
                # Calculate example position sizes
                current_price = self.get_current_price(symbol)
                if current_price > 0:
                    min_qty_for_min_value = rules['min_notional_value'] / current_price
                    print(f"   Current Price: ${current_price}")
                    print(f"   Min Qty for Min Value: {min_qty_for_min_value:.6f}")
                    
                    # Example: 5% of $1000 = $50
                    example_value = 50.0
                    example_qty = example_value / current_price
                    
                    # Check if qty_step is valid to avoid division by zero
                    if rules['qty_step'] > 0:
                        steps = example_qty / rules['qty_step']
                        rounded_qty = round(steps) * rules['qty_step']
                        print(f"   Example 5% Position: {rounded_qty:.6f} (Value: ${rounded_qty * current_price:.2f})")
                    else:
                        print(f"   Example 5% Position: {example_qty:.6f} (Value: ${example_qty * current_price:.2f})")
                        print(f"   ⚠️ Warning: Invalid quantity step ({rules['qty_step']})")
                else:
                    print(f"   Current Price: Unable to fetch")
            else:
                print(f"\n❌ No valid trading rules for {symbol}")
    
    def get_current_price(self, symbol):
        """Get current price for a symbol"""
        try:
            result, error = self.make_request("GET", "/v5/market/tickers", 
                                            params={"category": "linear", "symbol": symbol})
            if result and 'list' in result and result['list']:
                return float(result['list'][0].get('lastPrice', 0))
            return 0
        except Exception as e:
            print(f"❌ Error getting price for {symbol}: {e}")
            return 0

# Test with a few symbols
if __name__ == "__main__":
    # Initialize the trading rules checker
    rules_checker = BybitTradingRules()
    
    # First, get all symbols information and cache it
    print("Fetching all symbols information...")
    if rules_checker.get_all_symbols_info():
        print("✅ Successfully cached symbol information")
    else:
        print("❌ Failed to cache symbol information")
    
    # Test with a few symbols - some that failed and some common ones
    test_symbols = [
        "0GUSDT",  # Failed in your logs
        "1000000BABYDOGEUSDT",  # Failed in your logs
        "BTCUSDT",  # Common symbol
        "ETHUSDT",  # Common symbol
        "SOLUSDT",  # Common symbol
    ]
    
    # Display the trading rules
    rules_checker.display_trading_rules(test_symbols)