from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Deduplicate Event Log") \
    .getOrCreate()

# Sample data
data = [
    (1, 'user1', 'click', '2021-01-01'),
    (2, 'user1', 'click', '2021-01-02'),
    (3, 'user2', 'view', '2021-01-01'),
    (4, 'user1', 'click', '2021-01-03'),
    (5, 'user2', 'view', '2021-01-03'),
    (6, 'user3', 'click', '2021-01-01')
]

# Create DataFrame
df = spark.createDataFrame(data, ["id", "user_id", "event_type", "event_date"])

# Define window specification
window_spec = Window.partitionBy("user_id", "event_type").orderBy(col("event_date").desc())

# Add row number column
df = df.withColumn("row_num", row_number().over(window_spec))

# Filter to keep only the latest record per user_id and event_type
deduplicated_df = df.filter(col("row_num") == 1).drop("row_num")

# Show the result
deduplicated_df.show()

# Stop the Spark session
spark.stop()
