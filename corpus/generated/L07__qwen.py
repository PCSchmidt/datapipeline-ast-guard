import polars as pl

# Sample clickstream data
data = {
    'user_id': [1, 1, 1, 2, 2, 3, 3],
    'timestamp': ['2023-04-01 10:00:00', '2023-04-01 10:15:00', '2023-04-01 11:00:00', '2023-04-01 12:00:00', '2023-04-01 12:30:00', '2023-04-01 13:00:00', '2023-04-01 13:30:00']
}

# Convert data to a Polars DataFrame
df = pl.DataFrame(data)

# Convert timestamp column to datetime
df = df.with_column(pl.col('timestamp').str.to_datetime())

# Calculate the time difference between consecutive timestamps
df = df.with_column(
    pl.col('timestamp').shift(-1).alias('next_timestamp')
).with_column(
    pl.col('next_timestamp').dt.diff().alias('time_diff')
).drop_nulls(subset=['time_diff'])

# Assign session IDs based on the 30-minute inactivity gap
df = df.with_column(
    pl.when(pl.col('time_diff') > pl.duration(minutes=30)).then(pl.lit(1))
    .otherwise(pl.lit(0))
).with_column(
    pl.col('session_id').cumsum().shift_and_fill(0, 0).alias('session_id')
).drop(['time_diff', 'next_timestamp'])

print(df)
