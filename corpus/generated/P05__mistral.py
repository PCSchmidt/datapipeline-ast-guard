import pandas as pd
from collections import defaultdict
import json

# Assuming logs.json is your JSON file
data = []
with open('logs.json', 'r') as f:
    for line in f:
        log = json.loads(line)
        data.append(log)

# Flatten the nested fields
df = pd.DataFrame(data)
df['service'] = df['service'].apply(lambda x: x['service'])
df['error'] = df['error'].apply(lambda x: x['error'])
df['time'] = pd.to_datetime(df['time'], unit='s')

# Group by service, hour, and error to count the errors per service per hour
grouped = df.groupby(['service', df['time'].dt.normalize('h'), 'error']).size()

# Reshape the data to have one row per service, hour, and error
grouped_df = grouped.reset_index().melt(id_vars=['service', 'hour'], var_name='error', value_name='count')

# Save the result as a CSV file
grouped_df.to_csv('errors_per_service_per_hour.csv', index=False)
