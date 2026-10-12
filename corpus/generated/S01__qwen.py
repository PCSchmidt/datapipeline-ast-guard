from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, sum
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Daily Sales Revenue Calculation") \
    .getOrCreate()

# Define the schema for the CSV files
schema = StructType([
    StructField("Date", StringType(), True),
    StructField("Region", StringType(), True),
    StructField("SalesAmount", DoubleType(), True)
])

# Read the CSV files from the landing folder
landing_folder = "/path/to/landing/folder"
df = spark.read.csv(landing_folder, header=True, schema=schema)

# Convert the Date column to a date format
df = df.withColumn("Date", to_date(col("Date"), "yyyy-MM-dd"))

# Group by Date and Region, and compute the sum of SalesAmount
result_df = df.groupBy("Date", "Region").agg(sum("SalesAmount").alias("Revenue"))

# Write the result as Parquet partitioned by Date
output_folder = "/path/to/output/folder"
result_df.write.parquet(output_folder, partitionBy=["Date"], mode="overwrite")

# Stop the Spark session
spark.stop()
