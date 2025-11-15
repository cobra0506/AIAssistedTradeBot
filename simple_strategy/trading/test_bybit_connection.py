import os
import requests
import json
import time
import hmac
import hashlib
from urllib.parse import urlencode

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
    # For GET requests with query parameters, include them in the signature
    if method == "GET" and params:
        # Sort parameters and encode them
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        param_str = timestamp + api_key + recv_window + query_string
    else:
        # For POST requests or GET without params
        param_str = timestamp + api_key + recv_window + str(body)
    
    signature = hmac.new(
        api_secret.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return signature

def test_bybit_connection():
    """Test Bybit demo API connection using the WORKING direct HTTP method"""
    print("=== Testing Bybit Demo API Connection ===")
    
    # Load API credentials
    api_key, api_secret = load_api_credentials()
    BASE_URL = "https://api-demo.bybit.com"
    recv_window = "5000"  # 5 seconds
    
    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False
    
    print(f"API Key: {api_key[:10]}...")
    
    try:
        # Test 1: Server Time (public endpoint)
        print("\n--- Testing Server Time ---")
        url = f"{BASE_URL}/v5/market/time"
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ SUCCESS")
            print(f"Server time: {result['result']['timeSecond']}")
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
        
        # Test 2: Wallet Balance (private endpoint)
        print("\n--- Testing Wallet Balance ---")
        url = f"{BASE_URL}/v5/account/wallet-balance?accountType=UNIFIED"
        
        # Generate authentication headers
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
            print("✅ SUCCESS")
            # Extract USDT balance
            wallet_data = result['result']['list'][0]
            usdt_balance = wallet_data.get('totalAvailableBalance', '0')
            print(f"USDT Balance: {usdt_balance}")
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
        
        # Test 3: Market Tickers (public endpoint)
        print("\n--- Testing Market Tickers ---")
        url = f"{BASE_URL}/v5/market/tickers?category=linear"
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ SUCCESS")
            tickers_count = len(result['result']['list'])
            print(f"Fetched {tickers_count} tickers")
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
        
        # Test 4: Get Perpetual Symbols
        print("\n--- Testing Perpetual Symbols ---")
        url = f"{BASE_URL}/v5/market/instruments-info?category=linear"
        response = requests.get(url)
        result = response.json()
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ SUCCESS")
            symbols = result['result']['list']
            perpetual_symbols = [s['symbol'] for s in symbols if s.get('contractType') == 'PERPETUAL']
            print(f"Found {len(perpetual_symbols)} perpetual symbols")
            if len(perpetual_symbols) > 0:
                print(f"First 5 symbols: {perpetual_symbols[:5]}")
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
        
        print("\n=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == '__main__':
    test_bybit_connection()