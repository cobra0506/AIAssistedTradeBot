# simple_strategy/trading/test_available_endpoints_with_auth.py
import os
import sys
import requests
import json
import time
import hmac
import hashlib
from urllib.parse import urlencode, urlparse

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

def generate_signature(api_secret, timestamp, method, path, body='', params=None):
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

# Load API credentials
api_key, api_secret = load_api_credentials()
BASE_URL = "https://api-demo.bybit.com"
recv_window = "5000"  # 5 seconds

# List of endpoints to test
ENDPOINTS = [
    # Public endpoints (no authentication required)
    {"method": "GET", "path": "/v5/market/time", "name": "Server Time"},
    {"method": "GET", "path": "/v5/market/tickers?category=linear", "name": "Market Tickers"},
    
    # Private endpoints (authentication required)
    {"method": "GET", "path": "/v5/account/wallet-balance", "name": "Wallet Balance", "params": {"accountType": "UNIFIED"}},
    {"method": "GET", "path": "/v5/account/info", "name": "Account Info"},
    {"method": "GET", "path": "/v5/position/list", "name": "Position List", "params": {"category": "linear", "symbol": "BTCUSDT"}},
]

def test_endpoint(endpoint):
    # Handle query parameters
    params = endpoint.get('params', {})
    if params:
        query_string = urlencode(params)
        url = f"{BASE_URL}{endpoint['path']}?{query_string}"
    else:
        url = f"{BASE_URL}{endpoint['path']}"
    
    headers = {"Content-Type": "application/json"}
    
    if api_key and api_secret and endpoint['name'] not in ["Server Time", "Market Tickers"]:
        # Generate timestamp and signature for private endpoints
        timestamp = str(int(time.time() * 1000))
        
        # Generate signature
        signature = generate_signature(
            api_secret, 
            timestamp, 
            endpoint['method'], 
            endpoint['path'], 
            params=params
        )
        
        headers.update({
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        })
    
    try:
        if endpoint['method'] == "GET":
            response = requests.get(url, headers=headers)
        elif endpoint['method'] == "POST":
            response = requests.post(url, headers=headers, json=endpoint.get('data', {}))
        
        result = response.json()
        
        if response.status_code == 200 and result.get('retCode') == 0:
            return {"status": "✅ SUCCESS", "response": result}
        else:
            return {"status": "❌ FAILED", "response": result}
    except Exception as e:
        return {"status": "❌ ERROR", "response": str(e)}

def main():
    print("=== Testing Bybit Demo API Endpoints (With Corrected Auth) ===\n")
    print(f"API Key: {api_key[:10] if api_key else 'None'}...\n")
    
    available_endpoints = []
    failed_endpoints = []
    
    for endpoint in ENDPOINTS:
        print(f"--- Testing {endpoint['name']} ---")
        result = test_endpoint(endpoint)
        print(f"Status: {result['status']}")
        
        if result['status'] == "✅ SUCCESS":
            available_endpoints.append(endpoint['name'])
            # Show some sample data for successful endpoints
            if 'result' in result['response']:
                print(f"Sample data: {str(result['response']['result'])[:100]}...")
        else:
            error_msg = "Unknown error"
            if isinstance(result['response'], dict):
                error_msg = result['response'].get('retMsg', str(result['response']))
            else:
                error_msg = str(result['response'])
                
            failed_endpoints.append({
                "name": endpoint['name'],
                "error": error_msg
            })
            print(f"Error: {error_msg}")
        
        print()
    
    print("=== SUMMARY ===")
    print(f"✅ Available endpoints ({len(available_endpoints)}):")
    for endpoint in available_endpoints:
        print(f"  - {endpoint}")
    
    print(f"\n❌ Failed endpoints ({len(failed_endpoints)}):")
    for endpoint in failed_endpoints:
        print(f"  - {endpoint['name']}: {endpoint['error']}")

if __name__ == "__main__":
    main()