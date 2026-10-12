import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SalesRevenueByRegion") \
    .getOrCreate()

# Define the landing folder path
landing_folder = "/path/to/landing/folder"

# Read daily sales CSV files
df = spark.read.csv(f"{landing_folder}/*.csv", header=True, inferSchema=True)

# Convert the 'date' column to date type
df = df.withColumn("date", to_date(col("date"), "yyyy-MM-dd"))

# Calculate revenue per region per day
revenue_df = df.groupBy("date", "region").agg(sum("revenue").alias("total_revenue"))

# Write the result as Parquet partitioned by date
revenue_df.write.parquet("/path/to/output/folder", partitionBy="date")

# Stop the Spark session
spark.stop()
