import pandas as pd

# Sample data creation
data = {
    'sensor_id': ['A', 'A', 'A', 'A', 'A', 'A', 'A', 'B', 'B', 'B', 'B', 'B', 'B', 'B'],
    'timestamp': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07']),
    'reading': [10, 12, 11, 13, 14, 15, 16, 20, 22, 21, 23, 24, 25, 26]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Sort by sensor_id and timestamp
df.sort_values(by=['sensor_id', 'timestamp'], inplace=True)

# Compute rolling 7-day average
df['rolling_avg'] = df.groupby('sensor_id')['reading'].rolling(window=7).mean().reset_index(0, drop=True)

print(df)
