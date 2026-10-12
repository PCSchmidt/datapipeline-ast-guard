import json
import time
from collections import defaultdict
from itertools import groupby

def parse_log_file(file_path):
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            event = json.loads(line)
            service = event.get('service', 'unknown')
            timestamp = int(time.mktime(time.strptime(event['timestamp'], "%Y-%m-%d %H:%M:%S")))
            data.append((service, timestamp, event))
    return data

def count_errors_per_service_per_hour(data):
    count_dict = defaultdict(lambda: defaultdict(int))
    for service, timestamp, event in data:
        if event['status'] == 'error':
            count_dict[service][timestamp//3600] += 1
    return count_dict

def save_results_to_json(count_dict, output_file):
    with open(output_file, 'w') as f:
        json.dump(count_dict, f, indent=4, default=str)

if __name__ == "__main__":
    log_file = "path/to/your/logfile.jsonl"
    output_file = "path/to/output/errors_per_service_per_hour.json"

    data = parse_log_file(log_file)
    count_dict = count_errors_per_service_per_hour(data)
    save_results_to_json(count_dict, output_file)
