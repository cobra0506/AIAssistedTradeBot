import requests
import json
import os
import time
import hmac
import hashlib

def test_bybit_demo_api():
    """Test Bybit demo API with correct demo endpoints"""
    
    # Load accounts
    api_accounts_file = os.path.join(os.path.dirname(__file__), 'api_accounts.json')
    with open(api_accounts_file, 'r') as f:
        accounts = json.load(f)
    
    demo_account = accounts.get('demo_accounts', {}).get('bybit_demo')
    
    if not demo_account:
        print("❌ No demo account found")
        return False
    
    print("=== Testing Demo API (Correct Endpoints) ===")
    print(f"API Key: {demo_account['api_key'][:10]}...")
    
    # API credentials
    api_key = demo_account['api_key']
    api_secret = demo_account['api_secret']
    
    # Test 1: Server time (no auth needed)
    print("\n--- Test 1: Server Time (No Auth) ---")
    try:
        response = requests.get("https://api-demo.bybit.com/v5/public/time")
        result = response.json()
        
        if result.get('retCode') == 0:
            print("✅ SUCCESS: Server time endpoint works")
            print(f"Server time: {result.get('result', {}).get('time')}")
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    # Test 2: Account Info (auth required, but works for demo)
    print("\n--- Test 2: Account Info (Auth Required) ---")
    try:
        # Get current timestamp
        timestamp = str(int(time.time() * 1000))
        recv_window = '5000'
        
        # Create signature for account info
        param_str = timestamp + api_key + recv_window
        signature = hmac.new(
            api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-SIGN': signature,
            'X-BAPI-RECV-WINDOW': recv_window
        }
        
        response = requests.get("https://api-demo.bybit.com/v5/account/info", headers=headers)
        result = response.json()
        
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('retCode') == 0:
            print("✅ SUCCESS: Account info endpoint works")
            return True
        else:
            print(f"❌ FAILED: {result.get('retMsg', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == '__main__':
    test_bybit_demo_api()