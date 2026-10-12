import polars as pl

# Assuming df is your DataFrame
df = pl.read_csv("sensor_data.csv")

# Convert timestamp to datetime and sort the data
df = df.with_column(
    pl.datetime("strptime(timestamp, '%%Y-%%m-%%d %%H:%%M:%%S')")
    .alias("datetime")
)
df = df.sort(["sensor_id", "datetime"])

# Compute rolling 7-day mean for each sensor
rolled_mean = df.groupby(["sensor_id"]).agg(
    pl.col("reading").rolling(7, min_periods=1).mean().alias("rolling_7day_mean")
)

# Write the result to a new csv file
rolled_mean.write_csv("rolled_7day_mean.csv")
