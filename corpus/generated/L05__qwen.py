import json
from collections import defaultdict
from datetime import datetime

# Example log entry: '{"timestamp": "2023-04-01T12:34:56Z", "service": "serviceA", "level": "ERROR", "message": "Error message here"}'

# Initialize a dictionary to store the count of errors per service per hour
error_counts = defaultdict(lambda: defaultdict(int))

# Path to the log file
log_file_path = 'path_to_your_log_file.log'

# Open and read the log file
with open(log_file_path, 'r') as file:
    for line in file:
        log_entry = json.loads(line)
        timestamp = log_entry['timestamp']
        service = log_entry['service']
        level = log_entry['level']
        
        # Check if the log level is ERROR
        if level == 'ERROR':
            # Parse the timestamp to get the hour
            log_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
            hour = log_time.hour
            
            # Count the error
            error_counts[service][hour] += 1

# Print the error counts
for service, hour_counts in error_counts.items():
    print(f"Service: {service}")
    for hour, count in hour_counts.items():
        print(f"  Hour {hour}: {count} errors")
