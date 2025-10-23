import pandas as pd

# Load your data
df = pd.read_csv('data\ADAUSDT_1.csv')
df['datetime'] = pd.to_datetime(df['datetime'])

# Print the date range
print(f"Data starts: {df['datetime'].min()}")
print(f"Data ends: {df['datetime'].max()}")
print(f"Total rows: {len(df)}")