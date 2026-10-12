import pandas as pd

# Assuming df is your DataFrame
df = pd.DataFrame({
    'user_id': [1, 1, 2, 2, 1, 1],
    'event_type': ['A', 'B', 'C', 'A', 'B', 'C'],
    'timestamp': pd.date_range(start='2022-01-01', periods=6)
})

# Sort the DataFrame by user_id, event_type, and timestamp (in descending order for timestamp)
df = df.sort_values(by=['user_id', 'event_type', 'timestamp'], ascending=[True, True, False])

# Drop duplicates based on user_id and event_type
df.reset_index(drop=True, inplace=True)
