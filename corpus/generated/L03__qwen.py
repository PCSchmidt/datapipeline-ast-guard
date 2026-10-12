import polars as pl

# Assuming 'df' is your DataFrame with columns 'user_id', 'event_type', and 'timestamp'
df = pl.scan_csv("path_to_your_large_event_table.csv")

# Keep only the most recent row per user_id and event_type
df = df.with_column(
    pl.col("timestamp").cast(pl.Datetime)
).with_column(
    pl.col("row_num").over(["user_id", "event_type"], reverse=True).cast(pl.Int32)
).filter(pl.col("row_num") == 1).drop("row_num")

# Collect the result to materialize the DataFrame in memory
df.collect()
