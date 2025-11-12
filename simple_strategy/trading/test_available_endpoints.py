# simple_strategy/trading/test_available_endpoints.py
import os
import sys
import requests
import json

# Path to the API accounts JSON file
API_ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), 'api_accounts.json')

def load_api_credentials():
    try:
        with open(API_ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
            # Get the demo account credentials
            demo_account = accounts.get('demo_accounts', {}).get('bybit_demo', {})
            return demo_account.get('api_key'), demo_account.get('api_secret')
    except Exception as e:
        print(f"Error loading API credentials: {e}")
        return None, None

# Load API credentials from JSON file
API_KEY, API_SECRET = load_api_credentials()
BASE_URL = "https://api-demo.bybit.com"

# List of endpoints to test
ENDPOINTS = [
    # Public endpoints (no authentication required)
    {"method": "GET", "path": "/v5/market/time", "name": "Server Time"},
    {"method": "GET", "path": "/v5/market/tickers?category=linear", "name": "Market Tickers"},
    {"method": "GET", "path": "/v5/market/orderbook?category=linear&symbol=BTCUSDT", "name": "Order Book"},
    {"method": "GET", "path": "/v5/market/kline?category=linear&symbol=BTCUSDT&interval=60", "name": "Kline/Candlestick"},
    {"method": "GET", "path": "/v5/market/instruments-info?category=linear&symbol=BTCUSDT", "name": "Instruments Info"},
    
    # Private endpoints (authentication required)
    {"method": "GET", "path": "/v5/account/wallet-balance?accountType=UNIFIED", "name": "Wallet Balance"},
    {"method": "GET", "path": "/v5/account/info", "name": "Account Info"},
    {"method": "GET", "path": "/v5/position/list?category=linear&symbol=BTCUSDT", "name": "Position List"},
    {"method": "POST", "path": "/v5/order/create", "name": "Create Order", "data": {"category": "linear", "symbol": "BTCUSDT", "side": "Buy", "orderType": "Market", "qty": "0.001", "timeInForce": "ImmediateOrCancel"}},
]

def test_endpoint(endpoint):
    url = f"{BASE_URL}{endpoint['path']}"
    headers = {"Content-Type": "application/json"}
    
    if API_KEY and API_SECRET:
        headers["X-BAPI-API-KEY"] = API_KEY
        # Note: For private endpoints, we would need to add signature generation here
        # For simplicity, we're just testing if the endpoint exists and accepts our key
    
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
    print("=== Testing Bybit Demo API Endpoints ===\n")
    print(f"API Key: {API_KEY[:10] if API_KEY else 'None'}...\n")
    
    available_endpoints = []
    failed_endpoints = []
    
    for endpoint in ENDPOINTS:
        print(f"--- Testing {endpoint['name']} ---")
        result = test_endpoint(endpoint)
        print(f"Status: {result['status']}")
        
        if result['status'] == "✅ SUCCESS":
            available_endpoints.append(endpoint['name'])
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