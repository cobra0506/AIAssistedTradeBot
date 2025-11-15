import os
import json
import time
import requests
import hmac
import hashlib
from urllib.parse import urlencode

# Try to import optional libraries
try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    print("CCXT not available")

try:
    from pybit import HTTP, WebSocket
    PYBIT_AVAILABLE = True
except ImportError:
    PYBIT_AVAILABLE = False
    print("Pybit not available")

# Path to the API accounts JSON file
API_ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), 'api_accounts.json')

def load_api_credentials():
    try:
        with open(API_ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
            demo_account = accounts.get('demo_accounts', {}).get('bybit_demo', {})
            return demo_account.get('api_key'), demo_account.get('api_secret')
    except Exception as e:
        print(f"Error loading API credentials: {e}")
        return None, None

def generate_signature(api_secret, api_key, recv_window, timestamp, method, path, body='', params=None):
    """Generate HMAC-SHA256 signature for Bybit API V5"""
    if method == "GET" and params:
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        param_str = timestamp + api_key + recv_window + query_string
    else:
        param_str = timestamp + api_key + recv_window + str(body)
    
    signature = hmac.new(
        api_secret.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def test_direct_http_method():
    """Test connection using direct HTTP requests (currently working method)"""
    print("\n=== METHOD 1: Direct HTTP Requests ===")
    
    api_key, api_secret = load_api_credentials()
    BASE_URL = "https://api-demo.bybit.com"
    recv_window = "5000"
    
    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False
    
    try:
        # Test wallet balance
        url = f"{BASE_URL}/v5/account/wallet-balance?accountType=UNIFIED"
        timestamp = str(int(time.time() * 1000))
        signature = generate_signature(api_secret, api_key, recv_window, timestamp, "GET", "/v5/account/wallet-balance", params={"accountType": "UNIFIED"})
        
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('retCode') == 0:
            wallet_data = result['result']['list'][0]
            usdt_balance = wallet_data.get('totalAvailableBalance', '0')
            print(f"✅ SUCCESS - USDT Balance: {usdt_balance}")
            return True
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_ccxt_method():
    """Test connection using CCXT library"""
    print("\n=== METHOD 2: CCXT Library ===")
    
    if not CCXT_AVAILABLE:
        print("❌ CCXT not installed")
        return False
    
    api_key, api_secret = load_api_credentials()
    
    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False
    
    try:
        # Try different CCXT configurations
        configs = [
            # Configuration 1: Basic with demo URLs
            {
                'name': 'Basic with demo URLs',
                'config': {
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'urls': {
                        'api': {
                            'public': 'https://api-demo.bybit.com',
                            'private': 'https://api-demo.bybit.com',
                        }
                    }
                }
            },
            # Configuration 2: With sandbox mode
            {
                'name': 'With sandbox mode',
                'config': {
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'sandbox': True,
                    'urls': {
                        'api': {
                            'public': 'https://api-demo.bybit.com',
                            'private': 'https://api-demo.bybit.com',
                        }
                    }
                }
            },
            # Configuration 3: With linear default type
            {
                'name': 'With linear default type',
                'config': {
                    'apiKey': api_key,
                    'secret': api_secret,
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'linear',
                    },
                    'urls': {
                        'api': {
                            'public': 'https://api-demo.bybit.com',
                            'private': 'https://api-demo.bybit.com',
                        }
                    }
                }
            }
        ]
        
        for cfg in configs:
            print(f"\nTrying: {cfg['name']}")
            try:
                exchange = ccxt.bybit(cfg['config'])
                balance = exchange.fetch_balance()
                usdt_balance = balance['total']['USDT']
                print(f"✅ SUCCESS - USDT Balance: {usdt_balance}")
                return True
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
        
        print("❌ All CCXT configurations failed")
        return False
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_pybit_method():
    """Test connection using Pybit library"""
    print("\n=== METHOD 3: Pybit Library ===")
    
    if not PYBIT_AVAILABLE:
        print("❌ Pybit not installed")
        return False
    
    api_key, api_secret = load_api_credentials()
    
    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False
    
    try:
        # Initialize Pybit session for demo trading
        session = HTTP(
            testnet=True,  # This should use demo environment
            api_key=api_key,
            api_secret=api_secret
        )
        
        # Get wallet balance
        result = session.get_wallet_balance(accountType="UNIFIED")
        
        if result['retCode'] == 0:
            wallet_data = result['result']['list'][0]
            usdt_balance = wallet_data.get('totalAvailableBalance', '0')
            print(f"✅ SUCCESS - USDT Balance: {usdt_balance}")
            return True
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("=== Testing All Bybit API Connection Methods ===\n")
    
    # Test all methods
    methods = [
        ("Direct HTTP", test_direct_http_method),
        ("CCXT", test_ccxt_method),
        ("Pybit", test_pybit_method)
    ]
    
    results = {}
    for name, test_func in methods:
        results[name] = test_func()
    
    # Summary
    print("\n=== SUMMARY ===")
    for method, result in results.items():
        status = "✅ WORKING" if result else "❌ NOT WORKING"
        print(f"{method}: {status}")
    
    # Recommendation
    print("\n=== RECOMMENDATION ===")
    working_methods = [name for name, result in results.items() if result]
    
    if working_methods:
        print(f"Working methods: {', '.join(working_methods)}")
        if "Direct HTTP" in working_methods:
            print("RECOMMENDATION: Use Direct HTTP method for now (most reliable)")
    else:
        print("No methods are working. Check API credentials and network.")

if __name__ == '__main__':
    main()