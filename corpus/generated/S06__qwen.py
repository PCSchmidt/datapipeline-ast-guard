from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, explode, hour, minute, dayofmonth, month, year, count
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType

# Initialize Spark session
spark = SparkSession.builder.appName("LogProcessor").getOrCreate()

# Define schema for JSON logs
log_schema = StructType([
    StructField("timestamp", TimestampType(), True),
    StructField("service", StringType(), True),
    StructField("level", StringType(), True),
    StructField("message", StringType(), True),
    StructField("details", StructType([
        StructField("error_code", IntegerType(), True),
        StructField("error_message", StringType(), True)
    ]), True)
])

# Load JSON logs
logs_df = spark.read.json("path/to/logs.json", schema=log_schema)

# Flatten nested fields
flattened_df = logs_df.select(
    col("timestamp"),
    col("service"),
    col("level"),
    col("message"),
    col("details.error_code"),
    col("details.error_message")
)

# Convert timestamp to hour and minute
flattened_df = flattened_df.withColumn("hour", hour(col("timestamp"))).withColumn("minute", minute(col("timestamp")))

# Filter for errors
error_df = flattened_df.filter(col("level") == "ERROR")

# Count errors per service per hour
error_count_df = error_df.groupBy("service", "hour").count()

# Show the result
error_count_df.show()
