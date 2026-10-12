import pandas as pd
from datetime import timedelta

def assign_session_ids(df, gap=timedelta(minutes=30)):
    df['session_id'] = 0
    session_start = df.loc[0, 'timestamp']
    session_id = 1

    for index, row in df.iterrows():
        if (row['timestamp'] - session_start) > gap:
            session_start = row['timestamp']
            session_id += 1

        df.at[index, 'session_id'] = session_id
        session_start = row['timestamp']

    return df

# Sample clickstream data
clickstream = pd.DataFrame({
    'timestamp': ['2022-01-01 10:00:00', '2022-01-01 10:01:00', '2022-01-01 10:02:00',
                  '2022-01-01 10:15:00', '2022-01-01 10:16:00', '2022-01-01 10:17:00',
                  '2022-01-01 10:45:00', '2022-01-01 10:46:00', '2022-01-01 10:47:00',
                  '2022-01-01 11:15:00', '2022-01-01 11:16:00', '2022-01-01 11:17:00'],
    'ip_address': ['192.168.1.1', '192.168.1.1', '192.168.1.1',
                   '192.168.1.2', '192.168.1.2', '192.168.1.2',
                   '192.168.1.1', '192.168.1.1', '192.168.1.1',
                   '192.168.1.2', '192.168.1.2', '192.168.1.2']
})

clickstream['timestamp'] = pd.to_datetime(clickstream['timestamp'])
clickstream = assign_session_ids(clickstream)

print(clickstream)
