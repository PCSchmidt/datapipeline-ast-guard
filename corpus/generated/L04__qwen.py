import polars as pl

# Sample data
data = {
    'sensor_id': [1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2],
    'timestamp': [
        '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07',
        '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07'
    ],
    'reading': [10, 15, 13, 18, 17, 20, 22, 12, 14, 16, 19, 21, 23, 25]
}

# Create a DataFrame
df = pl.DataFrame(data)

# Convert timestamp to datetime
df = df.with_column(pl.col('timestamp').str.strptime(pl.Date, '%Y-%m-%d'))

# Sort by sensor_id and timestamp
df = df.sort(['sensor_id', 'timestamp'])

# Compute rolling 7-day mean
df = df.with_column(
    pl.col('rolling_mean').rolling_mean(window_size=7, min_periods=1)
)

print(df)
