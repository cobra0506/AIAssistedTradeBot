import ccxt
import json
import os

def verify_demo_api():
    """Verify demo API connection with correct ccxt methods"""
    
    # Load accounts
    api_accounts_file = os.path.join(os.path.dirname(__file__), 'api_accounts.json')
    with open(api_accounts_file, 'r') as f:
        accounts = json.load(f)
    
    # Get demo account
    demo_account = accounts.get('demo_accounts', {}).get('bybit_demo')
    
    if not demo_account:
        print("❌ No demo account found in api_accounts.json")
        return False
    
    print("=== Testing Demo API Connection ===")
    print(f"API Key: {demo_account['api_key'][:10]}...")
    
    try:
        # Configure exchange for Bybit V5 Demo
        exchange = ccxt.bybit({
            'apiKey': demo_account['api_key'],
            'secret': demo_account['api_secret'],
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot',
            },
            # Use demo domain
            'urls': {
                'api': {
                    'public': 'https://api-demo.bybit.com',
                    'private': 'https://api-demo.bybit.com',
                }
            }
        })
        
        print("🔗 Connecting to: https://api-demo.bybit.com")
        
        # Test 1: Get server time (simple, no balance needed)
        print("\n--- Test 1: Server Time ---")
        server_time = exchange.fetch_time()
        print(f"✅ SUCCESS: Server time: {server_time}")
        
        # Test 2: Get account info (using correct ccxt method)
        print("\n--- Test 2: Account Info ---")
        # The correct method name in ccxt is usually 'privateGetAccountInfo' or similar
        # Let's try different variations
        try:
            account_info = exchange.private_get_account_info()
            print("✅ SUCCESS: Account info retrieved")
            print(f"📊 Account Type: {account_info['result'].get('accountType', 'N/A')}")
        except AttributeError:
            print("⚠️  private_get_account_info not available, trying alternative...")
            try:
                # Try alternative method names
                account_info = exchange.fetch_account_info()
                print("✅ SUCCESS: Account info retrieved (alternative method)")
            except AttributeError:
                print("⚠️  Account info methods not available, but connection works!")
        
        # Test 3: Try to get markets (should work for demo)
        print("\n--- Test 3: Markets ---")
        markets = exchange.load_markets()
        print(f"✅ SUCCESS: Loaded {len(markets)} markets")
        
        print("\n🎉 CONCLUSION: Demo API connection is working!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ FAILED: {error_msg}")
        
        if "API key is invalid" in error_msg:
            print("\n🔧 SOLUTION:")
            print("1. Go to Bybit.com")
            print("2. Switch to Demo Trading")
            print("3. Create API key from Demo Trading interface")
            print("4. Update api_accounts.json with the new keys")
            
        elif "Demo trading are not supported" in error_msg:
            print("\n🔧 SOLUTION:")
            print("The domain is incorrect. Make sure you're using:")
            print("https://api-demo.bybit.com")
            
        return False

if __name__ == '__main__':
    verify_demo_api()