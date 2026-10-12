from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.dataset import DataFrame

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Data Quality Report') \
    .config("spark.sql.shuffle.partitions", 200) \
    .getOrCreate()

# Read the large table
df = spark.read.format("parquet").option("inferSchema", "true").load("path/to/your/large_table")

# Take a small random sample of the table
sample_df = df.limit(100000).randomSplit([0.01], seed=42)
sample_df = sample_df[0]

# Calculate summary statistics
stats_df = sample_df.stat().describe()

# Print the summary statistics
stats_df.show()

# Save the summary statistics to a Parquet file
stats_df.write.format("parquet").save("path/to/save/data_quality_report")

# Close the SparkSession
spark.stop()
