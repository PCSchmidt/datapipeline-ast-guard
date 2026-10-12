import pandas as pd

# Sample data creation
data = {
    'sensor_id': ['sensor1', 'sensor1', 'sensor1', 'sensor1', 'sensor1', 'sensor1', 'sensor1', 'sensor2', 'sensor2', 'sensor2', 'sensor2', 'sensor2', 'sensor2', 'sensor2'],
    'timestamp': pd.to_datetime(['2023-04-01', '2023-04-02', '2023-04-03', '2023-04-04', '2023-04-05', '2023-04-06', '2023-04-07', '2023-04-01', '2023-04-02', '2023-04-03', '2023-04-04', '2023-04-05', '2023-04-06', '2023-04-07']),
    'reading': [10, 12, 11, 13, 14, 15, 16, 20, 22, 21, 23, 24, 25, 26]
}

# Creating DataFrame
df = pd.DataFrame(data)

# Sorting the DataFrame by sensor_id and timestamp
df.sort_values(by=['sensor_id', 'timestamp'], inplace=True)

# Calculating rolling 7-day mean
df['rolling_mean'] = df.groupby('sensor_id')['reading'].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)

print(df)
