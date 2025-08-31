import requests
import json
import os
from datetime import datetime

def test_symbol_fetching():
    """Test fetching symbols from Bybit API directly"""
    
    # API settings
    API_BASE_URL = 'https://api.bybit.com'
    
    print("="*60)
    print("TESTING SYMBOL FETCHING FROM BYBIT")
    print("="*60)
    
    # Test 1: Basic API call without filters
    print("\n1. Testing basic API call without filters...")
    url = f"{API_BASE_URL}/v5/market/instruments-info"
    params = {
        "category": "linear",
        "limit": 100
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Code: {data.get('retCode')}")
            print(f"Response Message: {data.get('retMsg')}")
            
            if data.get('retCode') == 0:
                items = data['result']['list']
                print(f"Total items returned: {len(items)}")
                
                # Print first 5 items to see structure
                print("\nFirst 5 items:")
                for i, item in enumerate(items[:5]):
                    print(f"  {i+1}. {item}")
                
                # Print all symbols to see what we're working with
                print("\nAll symbols in response:")
                all_symbols = [item['symbol'] for item in items]
                for symbol in all_symbols:
                    print(f"  {symbol}")
                
                # Filter for USDT perpetuals
                print("\nFiltered USDT perpetuals:")
                usdt_perpetuals = []
                for item in items:
                    if (item['symbol'].endswith('USDT') and 
                        item.get('contractType') == 'PERPETUAL'):
                        usdt_perpetuals.append(item['symbol'])
                
                print(f"Found {len(usdt_perpetuals)} USDT perpetuals:")
                for symbol in usdt_perpetuals:
                    print(f"  {symbol}")
            else:
                print(f"Error in response: {data}")
        else:
            print(f"HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 2: Try with pagination
    print("\n2. Testing with pagination...")
    cursor = None
    all_symbols = []
    page_count = 0
    
    while page_count < 3:  # Limit to 3 pages for testing
        params = {
            "category": "linear",
            "limit": 100,
            "cursor": cursor
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('retCode') == 0:
                    items = data['result']['list']
                    page_symbols = [item['symbol'] for item in items]
                    all_symbols.extend(page_symbols)
                    
                    print(f"Page {page_count + 1}: {len(page_symbols)} symbols")
                    
                    cursor = data['result'].get('nextPageCursor')
                    if not cursor:
                        print("No more pages available")
                        break
                    page_count += 1
                else:
                    print(f"Error in response: {data.get('retMsg')}")
                    break
            else:
                print(f"HTTP Error: {response.status_code}")
                break
                
        except Exception as e:
            print(f"Exception on page {page_count + 1}: {e}")
            break
    
    print(f"\nTotal symbols found across {page_count} pages: {len(all_symbols)}")
    
    # Test 3: Check specific fields that might be causing issues
    print("\n3. Checking specific fields in the data...")
    url = f"{API_BASE_URL}/v5/market/instruments-info"
    params = {
        "category": "linear",
        "limit": 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('retCode') == 0:
                items = data['result']['list']
                
                print("Checking fields in first item:")
                if items:
                    first_item = items[0]
                    for key, value in first_item.items():
                        print(f"  {key}: {value}")
                
                print("\nChecking contractType and status fields:")
                for i, item in enumerate(items):
                    symbol = item.get('symbol', 'N/A')
                    contract_type = item.get('contractType', 'N/A')
                    status = item.get('status', 'N/A')
                    print(f"  {i+1}. {symbol} - contractType: {contract_type}, status: {status}")
    
    except Exception as e:
        print(f"Exception: {e}")
    
    # Test 4: Try a different category
    print("\n4. Testing with 'spot' category...")
    params = {
        "category": "spot",
        "limit": 10
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Response Code: {data.get('retCode')}")
            print(f"Response Message: {data.get('retMsg')}")
            
            if data.get('retCode') == 0:
                items = data['result']['list']
                print(f"Total items returned: {len(items)}")
                
                print("\nFirst 10 spot symbols:")
                for i, item in enumerate(items[:10]):
                    print(f"  {i+1}. {item.get('symbol')}")
    
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_symbol_fetching()