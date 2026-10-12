from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, mean, stddev, min, max

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Data Quality Report") \
    .getOrCreate()

# Load your large table
large_table = spark.read.format("parquet").load("path_to_large_table")

# Sample the data (e.g., 1% of the data)
sampled_data = large_table.sample(False, 0.01, seed=42)

# Define a list of columns to analyze
columns_to_analyze = ["column1", "column2", "column3"]

# Create a summary statistics report
summary_report = sampled_data.select(
    col(column).alias(column) for column in columns_to_analyze
).agg(
    count(column).alias(f"count_{column}"),
    mean(column).alias(f"mean_{column}"),
    stddev(column).alias(f"stddev_{column}"),
    min(column).alias(f"min_{column}"),
    max(column).alias(f"max_{column}")
).collect()

# Print the summary report
for row in summary_report:
    for column in columns_to_analyze:
        print(f"{column}:")
        print(f"  Count: {row[f'count_{column}']}")
        print(f"  Mean: {row[f'mean_{column}']}")
        print(f"  Standard Deviation: {row[f'stddev_{column}']}")
        print(f"  Min: {row[f'min_{column}']}")
        print(f"  Max: {row[f'max_{column}']}")
        print("-" * 40)

# Stop the Spark session
spark.stop()
