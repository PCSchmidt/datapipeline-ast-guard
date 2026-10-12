import polars as pl
from datetime import datetime

# Load the JSON log file
log_file_path = 'path_to_your_log_file.jsonl'
df = pl.read_json(log_file_path, lines=True)

# Convert the timestamp column to datetime
df = df.with_column(pl.col("timestamp").str.strptime(pl.Date, "%Y-%m-%dT%H:%M:%S.%fZ"))

# Extract hour from the timestamp
df = df.with_column(pl.col("timestamp").dt.hour.alias("hour"))

# Filter for error messages
df = df.filter(pl.col("message").str.contains("ERROR", case=False))

# Group by service and hour, then count the errors
result = df.groupby(["service", "hour"]).agg(pl.col("message").count().alias("error_count"))

# Sort the result by service and hour
result = result.sort(["service", "hour"])

# Print the result
print(result)
