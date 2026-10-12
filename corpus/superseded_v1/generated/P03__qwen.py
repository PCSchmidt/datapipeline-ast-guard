import pandas as pd

# Sample data
data = {
    'user_id': [1, 1, 2, 2, 3, 3, 3],
    'event_type': ['login', 'login', 'login', 'logout', 'login', 'logout', 'click'],
    'timestamp': ['2021-01-01 12:00:00', '2021-01-01 12:01:00', '2021-01-01 12:02:00', '2021-01-01 12:03:00', '2021-01-01 12:04:00', '2021-01-01 12:05:00', '2021-01-01 12:06:00']
}

# Convert timestamp to datetime
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Drop duplicates keeping the latest record
df_latest = df.drop_duplicates(subset=['user_id', 'event_type'], keep='last')

# Sort by user_id and timestamp to ensure order
df_latest = df_latest.sort_values(by=['user_id', 'timestamp']).reset_index(drop=True)

print(df_latest)
