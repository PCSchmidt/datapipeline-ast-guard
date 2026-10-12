from pyspark.sql import SparkSession
from pyspark.sql.functions import col, pivot

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Pivot Revenue Data") \
    .getOrCreate()

# Sample data
data = [
    ("Product A", "Jan", 1000),
    ("Product A", "Feb", 1500),
    ("Product B", "Jan", 2000),
    ("Product B", "Feb", 2500),
    ("Product A", "Mar", 1200),
    ("Product B", "Mar", 2200)
]

# Create DataFrame
df = spark.createDataFrame(data, ["Product Line", "Month", "Revenue"])

# Pivot the data
pivot_df = df.groupBy("Product Line").pivot("Month").sum("Revenue")

# Show the result
pivot_df.show()
