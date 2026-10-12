import pandas as pd

# Sample clickstream data
data = {
    'user_id': [1, 1, 1, 1, 2, 2, 2],
    'timestamp': ['2023-01-01 12:00:00', '2023-01-01 12:05:00', '2023-01-01 14:00:00', '2023-01-01 14:30:00', '2023-01-01 15:00:00', '2023-01-01 15:30:00', '2023-01-01 16:00:00']
}

# Convert timestamp to datetime
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort by user_id and timestamp
df = df.sort_values(by=['user_id', 'timestamp'])

# Assign session_id
session_id = 1
df['session_id'] = None

for i in range(1, len(df)):
    if df['user_id'][i] == df['user_id'][i-1] and (df['timestamp'][i] - df['timestamp'][i-1]).seconds <= 1800:
        df.at[i, 'session_id'] = df.at[i-1, 'session_id']
    else:
        df.at[i, 'session_id'] = session_id
        session_id += 1

print(df)
