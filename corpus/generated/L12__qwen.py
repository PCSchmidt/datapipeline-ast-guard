import polars as pl

# Define the path to your Parquet dataset
parquet_path = "path/to/your/large_dataset.parquet"

# Lazily read the Parquet dataset
df = pl.scan_parquet(parquet_path)

# Perform aggregation, for example, summing up a column named 'value'
aggregated_df = df.groupby("category").agg(pl.sum("value").alias("total_value"))

# Write the aggregated result to a new Parquet file
aggregated_df.write_parquet("path/to/output/aggregated_dataset.parquet")

print("Aggregation and writing completed successfully.")
