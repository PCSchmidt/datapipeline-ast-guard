from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session
spark = SparkSession.builder \
    .appName("ProductSnapshotComparison") \
    .getOrCreate()

# Read yesterday's and today's snapshots of the products table
yesterday_df = spark.read.csv("path/to/yesterday/products.csv", header=True, inferSchema=True)
today_df = spark.read.csv("path/to/today/products.csv", header=True, inferSchema=True)

# Rename today's DataFrame to include a timestamp or unique identifier
today_df = today_df.withColumn("snapshot_date", col("current_date"))

# Find added rows
added_rows = today_df.join(yesterday_df, on=["product_id"], how="left_anti")

# Find removed rows
removed_rows = yesterday_df.join(today_df, on=["product_id"], how="left_anti")

# Find changed rows
changed_rows = yesterday_df.join(today_df, on=["product_id"], how="inner") \
    .filter(yesterday_df["column1"] != today_df["column1"] | 
            yesterday_df["column2"] != today_df["column2"] | 
            # Add more columns to compare as needed
            col("column3") != col("column3"))

# Report the findings
print("Added Rows:")
added_rows.show()

print("\nRemoved Rows:")
removed_rows.show()

print("\nChanged Rows:")
changed_rows.show()

# Stop the Spark session
spark.stop()
