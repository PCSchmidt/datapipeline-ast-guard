import pandas as pd

def keep_most_recent_rows(event_df):
    """
    Keep only the most recent row per user_id and event_type in the given event DataFrame.

    :param event_df: DataFrame containing event data with columns 'user_id', 'event_type', and 'timestamp'
    :return: DataFrame with the most recent rows per user_id and event_type
    """
    # Sort the DataFrame by 'user_id', 'event_type', and 'timestamp' in descending order
    sorted_df = event_df.sort_values(by=['user_id', 'event_type', 'timestamp'], ascending=[True, True, False])
    
    # Drop duplicate rows based on 'user_id' and 'event_type', keeping the first occurrence (which is the most recent one after sorting)
    result_df = sorted_df.drop_duplicates(subset=['user_id', 'event_type'], keep='first')
    
    return result_df

# Example usage:
# Assuming 'events' is a DataFrame with columns 'user_id', 'event_type', and 'timestamp'
# recent_events = keep_most_recent_rows(events)
