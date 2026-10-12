import pandas as pd

# Sample clickstream data
data = {
    'user_id': [1, 1, 1, 2, 2, 2, 2],
    'timestamp': ['2023-01-01 10:00:00', '2023-01-01 10:15:00', '2023-01-01 10:45:00', '2023-01-01 11:00:00', '2023-01-01 11:15:00', '2023-01-01 11:45:00', '2023-01-01 12:30:00']
}

# Convert timestamp to datetime
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort by user_id and timestamp
df = df.sort_values(by=['user_id', 'timestamp'])

# Initialize session_id and previous_timestamp
df['session_id'] = None
df['previous_timestamp'] = df['timestamp'].shift(1)

# Calculate time difference in minutes
df['time_diff'] = (df['timestamp'] - df['previous_timestamp']).dt.total_seconds() / 60

# Assign session_id
df.loc[df['time_diff'] > 30, 'session_id'] = df['user_id']
df['session_id'].fillna(method='ffill', inplace=True)

# Drop intermediate columns
df.drop(columns=['previous_timestamp', 'time_diff'], inplace=True)

print(df)
