import time
import collections

def sessionize_data(data, session_length=1800):  # session_length in seconds (30 minutes)
    session_data = []
    current_session = []

    for event in data:
        user_id = event['user_id']
        timestamp = event['timestamp']
        current_session.append((timestamp, event))

        if len(current_session) > 1:
            last_event_timestamp, _ = current_session[-1]
            first_event_timestamp, _ = current_session[0]
            time_diff = int((last_event_timestamp - first_event_timestamp) / 60)

            if time_diff > session_length:
                session_data.append(current_session)
                current_session = [(timestamp, event)]

    # Add the last session for each user
    if current_session:
        session_data.append(current_session)

    return session_data

# Example usage
clickstream_data = [
    {'user_id': 1, 'timestamp': 1633028900},
    {'user_id': 1, 'timestamp': 1633029000},
    {'user_id': 1, 'timestamp': 1633029100},
    {'user_id': 1, 'timestamp': 1633029200},
    {'user_id': 1, 'timestamp': 1633029300},
    {'user_id': 1, 'timestamp': 1633030100},  # 10 minutes of inactivity
    {'user_id': 1, 'timestamp': 1633030200},
    {'user_id': 2, 'timestamp': 1633029000},
    {'user_id': 2, 'timestamp': 1633029100},
    {'user_id': 2, 'timestamp': 1633029200},
    {'user_id': 2, 'timestamp': 1633029300},
    {'user_id': 2, 'timestamp': 1633029400},
    {'user_id': 2, 'timestamp': 1633029500},
    {'user_id': 2, 'timestamp': 1633030000},  # 5 minutes of inactivity
    {'user_id': 2, 'timestamp': 1633030100},
]

sessionized_data = sessionize_data(clickstream_data)
print(sessionized_data)
