# simple_strategy/trading/BYBIT_DEMO_API.md
# Bybit Demo API Working Endpoints

## Authentication
All private endpoints require:
- API Key
- API Secret
- Timestamp (current time in milliseconds)
- Signature (HMAC-SHA256)

## Working Endpoints

### Public Endpoints (No Authentication Required)
1. **Server Time**
   - Method: GET
   - Path: `/v5/market/time`
   - Description: Get server time for synchronization

2. **Market Tickers**
   - Method: GET
   - Path: `/v5/market/tickers?category=linear`
   - Description: Get tickers for all linear markets

3. **Order Book**
   - Method: GET
   - Path: `/v5/market/orderbook?category=linear&symbol=BTCUSDT`
   - Description: Get order book data for a symbol

4. **Kline/Candlestick Data**
   - Method: GET
   - Path: `/v5/market/kline?category=linear&symbol=BTCUSDT&interval=60`
   - Description: Get historical candlestick data

5. **Instruments Info**
   - Method: GET
   - Path: `/v5/market/instruments-info?category=linear&symbol=BTCUSDT`
   - Description: Get instrument information

### Private Endpoints (Authentication Required)
1. **Wallet Balance**
   - Method: GET
   - Path: `/v5/account/wallet-balance?accountType=UNIFIED`
   - Description: Get wallet balance information

2. **Account Info**
   - Method: GET
   - Path: `/v5/account/info`
   - Description: Get account information

3. **Position List**
   - Method: GET
   - Path: `/v5/position/list?category=linear&symbol=BTCUSDT`
   - Description: Get current positions

## Authentication Implementation
```python
def generate_signature(api_secret, timestamp, method, path, params=None, body=''):
    if method == "GET" and params:
        sorted_params = sorted(params.items())
        query_string = urlencode(sorted_params)
        param_str = timestamp + api_key + recv_window + query_string
    else:
        param_str = timestamp + api_key + recv_window + str(body)
    
    return hmac.new(
        api_secret.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

Headers for Private Requests 
python

headers = {
    "Content-Type": "application/json",
    "X-BAPI-API-KEY": api_key,
    "X-BAPI-TIMESTAMP": timestamp,
    "X-BAPI-RECV-WINDOW": "5000",
    "X-BAPI-SIGN": signature
}