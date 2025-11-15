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

def test_post_signature():
    """Test different signature generation methods for POST requests"""
    print("=== Testing POST Signature Generation ===")
    
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
    
    # Method 1: Sorted JSON string (what we tried)
    print("\n--- Method 1: Sorted JSON String ---")
    try:
        timestamp = str(int(time.time() * 1000))
        body_str = json.dumps(order_data, separators=(',', ':'), sort_keys=True)
        param_str = timestamp + api_key + recv_window + body_str
        signature = hmac.new(api_secret.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        print(f"Body string: {body_str}")
        print(f"Param string: {param_str}")
        print(f"Signature: {signature}")
        
        # Try to make the request
        url = f"{BASE_URL}/v5/order/create"
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        response = requests.post(url, headers=headers, json=order_data)
        result = response.json()
        
        print(f"Response: {result}")
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ Method 1 SUCCESS!")
            return True
        else:
            print(f"❌ Method 1 FAILED: {result.get('retMsg', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Method 1 ERROR: {e}")
    
    # Method 2: Query string format (for POST)
    print("\n--- Method 2: Query String Format ---")
    try:
        timestamp = str(int(time.time() * 1000))
        # Convert POST data to query string format
        sorted_params = sorted(order_data.items())
        query_string = urlencode(sorted_params)
        param_str = timestamp + api_key + recv_window + query_string
        signature = hmac.new(api_secret.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        print(f"Query string: {query_string}")
        print(f"Param string: {param_str}")
        print(f"Signature: {signature}")
        
        # Try to make the request
        url = f"{BASE_URL}/v5/order/create"
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        response = requests.post(url, headers=headers, json=order_data)
        result = response.json()
        
        print(f"Response: {result}")
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ Method 2 SUCCESS!")
            return True
        else:
            print(f"❌ Method 2 FAILED: {result.get('retMsg', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Method 2 ERROR: {e}")
    
    # Method 3: No body in signature (just timestamp + key + recv_window)
    print("\n--- Method 3: No Body in Signature ---")
    try:
        timestamp = str(int(time.time() * 1000))
        param_str = timestamp + api_key + recv_window
        signature = hmac.new(api_secret.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        print(f"Param string: {param_str}")
        print(f"Signature: {signature}")
        
        # Try to make the request
        url = f"{BASE_URL}/v5/order/create"
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        response = requests.post(url, headers=headers, json=order_data)
        result = response.json()
        
        print(f"Response: {result}")
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ Method 3 SUCCESS!")
            return True
        else:
            print(f"❌ Method 3 FAILED: {result.get('retMsg', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Method 3 ERROR: {e}")

    # Method 4: Manual JSON body control
    print("\n--- Method 4: Manual JSON Body Control ---")
    try:
        timestamp = str(int(time.time() * 1000))
        # Create the exact JSON string we'll send
        body_str = json.dumps(order_data, separators=(',', ':'), sort_keys=True)
        param_str = timestamp + api_key + recv_window + body_str
        signature = hmac.new(api_secret.encode('utf-8'), param_str.encode('utf-8'), hashlib.sha256).hexdigest()
        
        print(f"Body string: {body_str}")
        print(f"Param string: {param_str}")
        print(f"Signature: {signature}")
        
        # Try to make the request with manual JSON body
        url = f"{BASE_URL}/v5/order/create"
        headers = {
            "Content-Type": "application/json",
            "X-BAPI-API-KEY": api_key,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": recv_window,
            "X-BAPI-SIGN": signature
        }
        
        # Send the exact JSON string we signed
        response = requests.post(url, headers=headers, data=body_str)
        result = response.json()
        
        print(f"Response: {result}")
        
        if response.status_code == 200 and result.get('retCode') == 0:
            print("✅ Method 4 SUCCESS!")
            return True
        else:
            print(f"❌ Method 4 FAILED: {result.get('retMsg', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Method 4 ERROR: {e}")
    
    return False

if __name__ == '__main__':
    test_post_signature()