import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import DataCollectionConfig
from .csv_manager import CSVManager

class HistoricalDataFetcher:
    def __init__(self, config: DataCollectionConfig, csv_manager: CSVManager):
        self.config = config
        self.csv_manager = csv_manager
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })
    
    def fetch_historical_klines(self, symbol: str, timeframe: str, 
                              start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch historical klines data from Bybit"""
        url = f"{self.config.API_BASE_URL}/v5/market/kline"
        
        params = {
            'category': 'linear',
            'symbol': symbol,
            'interval': timeframe,
            'start': int(start_time.timestamp() * 1000),
            'end': int(end_time.timestamp() * 1000),
            'limit': 1000
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['retCode'] != 0:
                print(f"API Error for {symbol} {timeframe}: {data['retMsg']}")
                return []
            
            klines = data['result']['list']
            formatted_data = []
            
            for kline in klines:
                formatted_data.append({
                    'timestamp': datetime.fromtimestamp(int(kline[0]) / 1000).isoformat(),
                    'open': kline[1],
                    'high': kline[2],
                    'low': kline[3],
                    'close': kline[4],
                    'volume': kline[5],
                    'turnover': kline[6]
                })
            
            return formatted_data
        
        except Exception as e:
            print(f"Error fetching data for {symbol} {timeframe}: {e}")
            return []
    
    def fetch_all_historical_data(self, days_back: int = 7) -> None:
        """Fetch historical data for all symbols and timeframes in parallel"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        tasks = []
        with ThreadPoolExecutor(max_workers=self.config.MAX_WORKERS) as executor:
            for symbol in self.config.SYMBOLS:
                for timeframe in self.config.TIMEFRAMES:
                    task = executor.submit(
                        self.fetch_historical_klines,
                        symbol, timeframe, start_time, end_time
                    )
                    tasks.append((symbol, timeframe, task))
            
            for symbol, timeframe, task in tasks:
                try:
                    data = task.result()
                    if data:
                        self.csv_manager.write_data(symbol, timeframe, data)
                        print(f"Fetched {len(data)} records for {symbol} {timeframe}")
                except Exception as e:
                    print(f"Error processing {symbol} {timeframe}: {e}")
                
                # Rate limiting
                time.sleep(60 / self.config.API_RATE_LIMIT)