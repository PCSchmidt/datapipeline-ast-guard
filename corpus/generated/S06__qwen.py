import json
from datetime import datetime

# Sample JSON data representing application logs
logs = '''
[
    {
        "timestamp": "2023-04-01T12:00:00Z",
        "service": "serviceA",
        "level": "error",
        "details": {
            "message": "Failed to connect to database"
        }
    },
    {
        "timestamp": "2023-04-01T12:00:30Z",
        "service": "serviceB",
        "level": "info",
        "details": {
            "message": "User logged in"
        }
    },
    {
        "timestamp": "2023-04-01T12:01:00Z",
        "service": "serviceA",
        "level": "error",
        "details": {
            "message": "Timeout error"
        }
    },
    {
        "timestamp": "2023-04-01T13:00:00Z",
        "service": "serviceA",
        "level": "info",
        "details": {
            "message": "Service started"
        }
    }
]
'''

# Load JSON data
data = json.loads(logs)

# Initialize a dictionary to store error counts per service per hour
error_counts = {}

# Process each log entry
for log in data:
    # Extract timestamp, service, and level
    timestamp = log['timestamp']
    service = log['service']
    level = log['level']
    
    # Check if the log is an error
    if level == 'error':
        # Convert timestamp to datetime object
        log_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        
        # Get the hour part of the timestamp
        hour = log_time.hour
        
        # Initialize the service in the dictionary if not already present
        if service not in error_counts:
            error_counts[service] = {}
        
        # Initialize the hour in the service dictionary if not already present
        if hour not in error_counts[service]:
            error_counts[service][hour] = 0
        
        # Increment the error count for this service and hour
        error_counts[service][hour] += 1

# Print the error counts per service per hour
for service, hours in error_counts.items():
    print(f"Service: {service}")
    for hour, count in hours.items():
        print(f"  Hour {hour}: {count} errors")
