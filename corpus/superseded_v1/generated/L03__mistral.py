import pandas as pd

# Read the input CSV file
input_file = 'events.csv'
data = pd.read_csv(input_file)

# Group the data by user_id and event_type, then sort by timestamps
grouped = data.groupby(['user_id', 'event_type']).sort_values('timestamp')

# Iterate through each group and keep only the latest row
latest_rows = grouped.first()

# Reset the index and set it to the original column 'user_id' and 'event_type'
latest_rows = latest_rows.reset_index(drop=True)
latest_rows.columns = ['user_id', 'event_type', 'timestamp']

# Write the result back to a CSV file
output_file = 'latest_events.csv'
latest_rows.to_csv(output_file, index=False)
