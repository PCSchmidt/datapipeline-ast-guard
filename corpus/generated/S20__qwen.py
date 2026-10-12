from pyspark.sql import SparkSession
from pyspark.sql.functions import date_format
from datetime import datetime, timedelta

# Initialize Spark session
spark = SparkSession.builder \
    .appName("LastMonthDataFilter") \
    .getOrCreate()

# Define paths
input_path = "s3a://your-bucket/input/last-month-data"
output_path = "s3a://your-bucket/output/filtered-data"

# Read last month's data
last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m")
df = spark.read.parquet(f"{input_path}/{last_month}")

# Filter the data (example: filter rows where 'status' is 'active')
filtered_df = df.filter(df.status == 'active')

# Write the result to another bucket
filtered_df.write.parquet(output_path)

# Stop Spark session
spark.stop()
