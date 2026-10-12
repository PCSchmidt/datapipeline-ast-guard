import polars as pl

# Load the Parquet dataset lazily
df = pl.read_parquet("data.parquet")

# Group the data by column_1 and calculate the sum
aggregated_df = df.groupby("column_1").agg([pl.col("*").sum()]).dropna()

# Write the aggregated result as a Parquet file
aggregated_df.write_parquet("aggregated_result.parquet")
