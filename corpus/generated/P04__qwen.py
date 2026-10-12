import pandas as pd

# Sample data
data = {
    'sensor_id': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07', 
                                '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07']),
    'reading': [10, 12, 11, 13, 14, 15, 16, 20, 22, 21, 23, 24, 25, 26]
}

df = pd.DataFrame(data)

# Set timestamp as the index
df.set_index('timestamp', inplace=True)

# Compute rolling 7-day average for each sensor
df['rolling_avg'] = df.groupby('sensor_id')['reading'].rolling(window=7, min_periods=1).mean()

print(df)
