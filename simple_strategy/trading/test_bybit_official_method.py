import os
import json
import time
import requests
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

def test_bybit_official_method():
    """Test using Bybit's official signature method"""
    print("=== Testing Bybit Official Method ===")
    
    api_key, api_secret = load_api_credentials()
    BASE_URL = "https://api-demo.bybit.com"
    recv_window = "5000"
    
    if not api_key or not api_secret:
        print("❌ No API credentials found")
        return False
    
    # Test order data
    order_data = {
        "category": "linear",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "orderType": "Market",
        "qty": "0.001",
        "timeInForce": "GTC"
    }
    
    print(f"Order data: {order_data}")
    
    try:
        timestamp = str(int(time.time() * 1000))
        
        # Method from Bybit V5 documentation
        # For POST requests, the signature should include the request body
        body_str = json.dumps(order_data, separators=(',', ':'))
        param_str = timestamp + api_key + recv_window + body_str
        
        signature = hmac.new(api_secret.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        print(f"Body string: {body_str}")
        print(f"Param string: {param_str}")
        print(f"Signature: {signature}")
        
        # Make the request
        url = f"{BASE_URL}/v5/order/create"
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        print(f"Request URL: {url}")
        print(f"Request Headers: {headers}")
        print(f"Request Body: {body_str}")
        
        response = requests.post(url, headers=headers, data=body_str)
        result = response.json()
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {result}")
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ SUCCESS!")
            return True
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == '__main__':
    test_bybit_official_method()