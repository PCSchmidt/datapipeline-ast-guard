from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, when, lit

# Initialize a SparkSession
spark = SparkSession.builder \
    .appName('Daily Sales Analysis') \
    .getOrCreate()

# Set the base path for the landing folder
base_path = 'path/to/your/landing/folder/'

# Define the pattern for the CSV files in the landing folder
file_pattern = base_path + '*.csv'

# Read all the CSV files using Spark's read.format('csv').option('header', 'true').load()
ds = spark.read.format('csv') \
    .option('header', 'true') \
    .option('inferSchema', 'true') \
    .option('multiLine', 'true') \
    .load(file_pattern)

# Compute revenue per region per day
revenue_df = ds.groupBy(['region', 'day']) \
    .agg(sum('sales').alias('revenue')) \
    .withColumnRenamed('day', 'date')

# Write the result as Parquet partitioned by date
output_path = 'path/to/your/output/folder/'
revenue_df.write.format('parquet') \
    .partitionBy('date') \
    .save(output_path)

# Stop the SparkSession
spark.stop()
