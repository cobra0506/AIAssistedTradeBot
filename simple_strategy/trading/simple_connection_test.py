import ccxt
import json
import os

def simple_connection_test():
    """Simple test to verify demo API connection works"""
    
    # Load accounts
    api_accounts_file = os.path.join(os.path.dirname(__file__), 'api_accounts.json')
    with open(api_accounts_file, 'r') as f:
        accounts = json.load(f)
    
    demo_account = accounts.get('demo_accounts', {}).get('bybit_demo')
    
    if not demo_account:
        print("❌ No demo account found")
        return False
    
    print("=== Simple Connection Test ===")
    print(f"API Key: {demo_account['api_key'][:10]}...")
    
    try:
        # Configure exchange
        exchange = ccxt.bybit({
            'apiKey': demo_account['api_key'],
            'secret': demo_account['api_secret'],
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'public': 'https://api-demo.bybit.com',
                    'private': 'https://api-demo.bybit.com',
                }
            }
        })
        
        # Just try to get server time - simplest possible test
        server_time = exchange.fetch_time()
        
        print("✅ SUCCESS: Demo API connection is working!")
        print(f"Server time: {server_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == '__main__':
    simple_connection_test()