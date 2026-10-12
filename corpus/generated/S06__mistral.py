import json
from collections import defaultdict
from datetime import datetime, timedelta

# Load the JSON application logs
with open('application_logs.json') as f:
    logs = json.load(f)

# Initialize counters for errors per service and per hour
error_counts = defaultdict(lambda: defaultdict(int))

# Iterate through logs and process each log entry
for log in logs:
    service = log['service']
    timestamp = datetime.strptime(log['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # Flatten the nested fields (assuming 'event' is the nested field containing 'error')
    event = log.get('event', {}).get('error', None)
    if event:
        error_counts[service][timestamp.strftime('%Y-%m-%d %H')] += 1

# Format and print the results
for service, service_counts in error_counts.items():
    print(f'Service: {service}')
    for hour, count in service_counts.items():
        print(f'Hour: {hour}, Count: {count}')
