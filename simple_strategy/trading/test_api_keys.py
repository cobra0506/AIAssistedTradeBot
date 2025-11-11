import unittest
import os
import sys
import json

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import ccxt

class TestAPIKeys(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        # Load API accounts
        api_accounts_file = os.path.join(os.path.dirname(__file__), 'api_accounts.json')
        with open(api_accounts_file, 'r') as f:
            self.accounts = json.load(f)
    
    def test_demo_accounts(self):
        """Test all demo API keys"""
        print("\n=== Testing Demo Accounts ===")
        
        demo_accounts = self.accounts.get('demo_accounts', {})
        self.assertGreater(len(demo_accounts), 0, "No demo accounts found")
        
        for account_name, account_info in demo_accounts.items():
            print(f"\nTesting: {account_name}")
            
            try:
                # Initialize Bybit exchange with V5 demo configuration
                exchange_config = {
                    'apiKey': account_info['api_key'],
                    'secret': account_info['api_secret'],
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                    },
                    # Use the correct demo domain for Bybit V5
                    'urls': {
                        'api': {
                            'public': 'https://api-demo.bybit.com',
                            'private': 'https://api-demo.bybit.com',
                        }
                    }
                }

                exchange = ccxt.bybit(exchange_config)
                
                # Test connection by fetching balance
                balance = exchange.fetch_balance()
                print(f"✅ SUCCESS: Connected successfully")
                print(f"   Balance: ${balance['total']['USDT']}")
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                
                # Provide helpful error message
                if "API key is invalid" in str(e):
                    print("   💡 TIP: Make sure you created this API key from the 'Demo Trading' interface")
                    print("   💡 TIP: Go to Bybit → Switch to Demo Trading → Create API key from there")
                elif "Demo trading are not supported" in str(e):
                    print("   💡 TIP: You need to use the demo domain: https://api-demo.bybit.com")
    
    def test_live_accounts(self):
        """Test all live API keys"""
        print("\n=== Testing Live Accounts ===")
        
        live_accounts = self.accounts.get('live_accounts', {})
        
        if not live_accounts:
            print("No live accounts found - skipping")
            return
        
        for account_name, account_info in live_accounts.items():
            print(f"\nTesting: {account_name}")
            
            try:
                # Initialize Bybit exchange for live trading
                exchange_config = {
                    'apiKey': account_info['api_key'],
                    'secret': account_info['api_secret'],
                    'enableRateLimit': True,
                    'options': {
                        'defaultType': 'spot',
                    }
                }

                exchange = ccxt.bybit(exchange_config)
                
                # Test connection by fetching balance
                balance = exchange.fetch_balance()
                print(f"✅ SUCCESS: Connected successfully")
                print(f"   Balance: ${balance['total']['USDT']}")
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")

if __name__ == '__main__':
    unittest.main(verbosity=2)