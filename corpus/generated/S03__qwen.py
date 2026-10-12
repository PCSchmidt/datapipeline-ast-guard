import pandas as pd

def deduplicate_event_log(event_log_path, output_path):
    # Load the event log into a pandas DataFrame
    event_log = pd.read_csv(event_log_path)
    
    # Sort the events by user_id, event_type, and timestamp in descending order
    event_log_sorted = event_log.sort_values(by=['user_id', 'event_type', 'timestamp'], ascending=[True, True, False])
    
    # Drop duplicates, keeping only the first occurrence (latest record per user_id and event_type)
    deduplicated_log = event_log_sorted.drop_duplicates(subset=['user_id', 'event_type'], keep='first')
    
    # Save the deduplicated log to a new CSV file
    deduplicated_log.to_csv(output_path, index=False)

# Example usage
deduplicate_event_log('path_to_event_log.csv', 'path_to_output_deduplicated_log.csv')
