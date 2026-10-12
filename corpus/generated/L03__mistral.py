import polars as pl

# Assuming df is your DataFrame
df = df.with_column(
    pl.col("row_number")
    .over(pl.window().partition_by("user_id", "event_type").order_by(pl.desc("timestamp")))
    .alias("row_number")
)

df = df.filter(pl.col("row_number") == 1)
