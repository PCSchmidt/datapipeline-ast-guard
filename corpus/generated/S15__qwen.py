from pyspark.sql import SparkSession
from pyspark.sql.functions import col, join
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Initialize Spark session
spark = SparkSession.builder.appName("EventEnrichment").getOrCreate()

# Define schema for the event stream
event_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# Sample event data
event_data = [
    ("e1", "click", "2023-04-01 12:00:00"),
    ("e2", "view", "2023-04-01 12:01:00"),
    ("e3", "click", "2023-04-01 12:02:00")
]

# Create DataFrame for event stream
events_df = spark.createDataFrame(event_data, schema=event_schema)

# Define schema for the lookup table
lookup_schema = StructType([
    StructField("event_type", StringType(), True),
    StructField("event_category", StringType(), True)
])

# Sample lookup data
lookup_data = [
    ("click", "interactions"),
    ("view", "interactions"),
    ("share", "interactions"),
    ("download", "downloads")
]

# Create DataFrame for the lookup table
lookup_df = spark.createDataFrame(lookup_data, schema=lookup_schema)

# Enrich events with attributes from the lookup table
enriched_events_df = events_df.join(lookup_df, on="event_type", how="left")

# Show the enriched DataFrame
enriched_events_df.show()

# Stop the Spark session
spark.stop()
