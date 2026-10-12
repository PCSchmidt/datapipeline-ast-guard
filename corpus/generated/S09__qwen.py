from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window

# Initialize Spark session
spark = SparkSession.builder.appName("SessionizeClickstream").getOrCreate()

# Sample data: user_id, timestamp, event
data = [
    ("user1", "2021-01-01 12:00:00", "click"),
    ("user1", "2021-01-01 12:15:00", "click"),
    ("user1", "2021-01-01 12:50:00", "click"),
    ("user2", "2021-01-01 13:00:00", "click"),
    ("user2", "2021-01-01 13:30:00", "click"),
    ("user2", "2021-01-01 14:00:00", "click"),
]

# Create DataFrame
df = spark.createDataFrame(data, ["user_id", "timestamp", "event"])

# Convert timestamp to datetime
df = df.withColumn("timestamp", col("timestamp").cast("timestamp"))

# Window specification for 30 minutes of inactivity
window_spec = window.rowsBetween(-29, 0).partitionBy("user_id").orderBy("timestamp")

# Create a column to identify sessions
df = df.withColumn("session_start", col("timestamp").min().over(window_spec))

# Filter out rows that are not the start of a session
df = df.filter(col("timestamp") == col("session_start"))

# Drop the temporary column
df = df.drop("session_start")

# Show the result
df.show(truncate=False)
