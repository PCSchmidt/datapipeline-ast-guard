import pandas as pd

# Assuming df is your DataFrame and it has columns 'user_id', 'event_type', 'timestamp'
df = pd.DataFrame({
    'user_id': [1, 1, 2, 2, 2, 1, 1],
    'event_type': ['A', 'B', 'C', 'A', 'B', 'D', 'C'],
    'timestamp': ['2021-01-01', '2021-01-02', '2021-01-03', '2021-01-04', '2021-01-05', '2021-01-06', '2021-01-07']
})

# Convert timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort the DataFrame by user_id, event_type, and timestamp (in descending order)
df_sorted = df.sort_values(by=['user_id', 'event_type', 'timestamp'], ascending=False)

# Drop the duplicate rows based on user_id and event_type
df_deduped = df_sorted.drop_duplicates(subset=['user_id', 'event_type'])

print(df_deduped)
