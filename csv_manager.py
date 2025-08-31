import csv
import os
from datetime import datetime
from typing import List, Dict, Any

class CSVManager:
    def __init__(self, data_dir: str, max_entries: int = 50):
        self.data_dir = data_dir
        self.max_entries = max_entries
        os.makedirs(data_dir, exist_ok=True)
    
    def get_file_path(self, symbol: str, timeframe: str) -> str:
        return os.path.join(self.data_dir, f"{symbol}_{timeframe}.csv")
    
    def write_data(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]) -> None:
        file_path = self.get_file_path(symbol, timeframe)
        
        # Read existing data
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                existing_data = list(reader)
        
        # Combine and sort by timestamp
        combined_data = existing_data + data
        combined_data.sort(key=lambda x: x['timestamp'])
        
        # Remove duplicates and keep only last max_entries
        unique_data = []
        seen_timestamps = set()
        for row in combined_data:
            if row['timestamp'] not in seen_timestamps:
                unique_data.append(row)
                seen_timestamps.add(row['timestamp'])
        
        final_data = unique_data[-self.max_entries:]
        
        # Write back to file
        if final_data:
            with open(file_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=final_data[0].keys())
                writer.writeheader()
                writer.writerows(final_data)
    
    def read_data(self, symbol: str, timeframe: str) -> List[Dict[str, Any]]:
        file_path = self.get_file_path(symbol, timeframe)
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)