# test_pagination.py
import asyncio
import aiohttp
import time
from datetime import datetime

async def test_pagination():
    """Test different pagination approaches for Bybit kline data"""
    
    symbol = "BTCUSDT"
    timeframe = "1"
    days = 2
    
    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)
    
    url = f"https://api.bybit.com/v5/market/kline"
    
    async with aiohttp.ClientSession() as session:
        all_candles = []
        
        # APPROACH 1: Fixed time chunks (8 hours per chunk)
        print("=== APPROACH 1: Fixed time chunks (8 hours per chunk) ===")
        
        chunk_duration = 8 * 60 * 60 * 1000  # 8 hours in milliseconds
        current_end = end_time
        
        while current_end > start_time:
            current_start = max(start_time, current_end - chunk_duration)
            
            params = {
                "category": "linear",
                "symbol": symbol,
                "interval": timeframe,
                "start": int(current_start),
                "end": int(current_end),
                "limit": 1000
            }
            
            try:
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    
                    if data.get("retCode") == 0:
                        candles = data["result"]["list"]
                        
                        if candles:
                            print(f"Chunk {datetime.fromtimestamp(current_start/1000)} to {datetime.fromtimestamp(current_end/1000)}: {len(candles)} candles")
                            
                            # Process candles
                            processed_candles = []
                            for candle in candles:
                                processed = {
                                    'timestamp': int(candle[0]),
                                    'open': float(candle[1]),
                                    'high': float(candle[2]),
                                    'low': float(candle[3]),
                                    'close': float(candle[4]),
                                    'volume': float(candle[5])
                                }
                                processed_candles.append(processed)
                            
                            all_candles.extend(processed_candles)
                            
                            # Update for next chunk
                            current_end = int(candles[-1][0]) - 1  # Oldest candle timestamp
                        else:
                            print("No candles returned")
                            break
                            
                        await asyncio.sleep(0.1)  # Small delay
                    else:
                        print(f"Error: {data.get('retMsg')}")
                        break
                        
            except Exception as e:
                print(f"Exception: {e}")
                break
        
        # Sort and display results
        all_candles.sort(key=lambda x: x['timestamp'])
        
        print(f"\n=== RESULTS ===")
        print(f"Total candles fetched: {len(all_candles)}")
        
        if all_candles:
            first_dt = datetime.fromtimestamp(all_candles[0]['timestamp'] / 1000)
            last_dt = datetime.fromtimestamp(all_candles[-1]['timestamp'] / 1000)
            print(f"Date range: {first_dt} to {last_dt}")
            
            # Expected candles for 2 days of 1-minute data
            expected_candles = days * 24 * 60
            print(f"Expected candles: {expected_candles}")
            print(f"Success rate: {len(all_candles) / expected_candles * 100:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_pagination())