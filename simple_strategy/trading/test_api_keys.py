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
                # Initialize Bybit exchange
                exchange = ccxt.bybit({
                    'apiKey': account_info['api_key'],
                    'secret': account_info['api_secret'],
                    'enableRateLimit': True,
                })
                
                # Test connection by fetching balance
                balance = exchange.fetch_balance()
                print(f"✅ SUCCESS: Connected successfully")
                print(f"   Balance: ${balance['total']['USDT']}")
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
    
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
                # Initialize Bybit exchange
                exchange = ccxt.bybit({
                    'apiKey': account_info['api_key'],
                    'secret': account_info['api_secret'],
                    'enableRateLimit': True,
                })
                
                # Test connection by fetching balance
                balance = exchange.fetch_balance()
                print(f"✅ SUCCESS: Connected successfully")
                print(f"   Balance: ${balance['total']['USDT']}")
                
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")

if __name__ == '__main__':
    unittest.main(verbosity=2)