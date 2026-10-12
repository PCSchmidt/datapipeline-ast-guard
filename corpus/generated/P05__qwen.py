import pandas as pd
import json
from datetime import datetime

# Sample JSON logs
json_logs = '''
[
    {"timestamp": "2023-04-01T12:00:00", "service": "ServiceA", "status": "error"},
    {"timestamp": "2023-04-01T12:00:00", "service": "ServiceB", "status": "success"},
    {"timestamp": "2023-04-01T12:01:00", "service": "ServiceA", "status": "error"},
    {"timestamp": "2023-04-01T12:01:00", "service": "ServiceC", "status": "error"},
    {"timestamp": "2023-04-01T12:02:00", "service": "ServiceA", "status": "success"},
    {"timestamp": "2023-04-01T12:02:00", "service": "ServiceB", "status": "error"}
]
'''

# Load JSON data into a DataFrame
logs = pd.read_json(json_logs)

# Convert timestamp to datetime
logs['timestamp'] = pd.to_datetime(logs['timestamp'])

# Extract hour and date
logs['hour'] = logs['timestamp'].dt.hour
logs['date'] = logs['timestamp'].dt.date

# Flatten nested fields if any (none in this example)

# Count errors per service per hour
error_counts = logs[(logs['status'] == 'error')].groupby(['date', 'hour', 'service']).size().reset_index(name='error_count')

print(error_counts)
