# Import necessary libraries
import pandas as pd
from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("EventEnrichment").getOrCreate()

# Sample data for events
events_data = [
    ("event1", "user1", "2023-01-01"),
    ("event2", "user2", "2023-01-02"),
    ("event3", "user1", "2023-01-03")
]

# Create DataFrame for events
events_df = spark.createDataFrame(events_data, ["event_id", "user_id", "event_date"])

# Sample data for user attributes
user_attributes_data = [
    ("user1", "admin", "New York"),
    ("user2", "user", "Los Angeles")
]

# Create DataFrame for user attributes
user_attributes_df = spark.createDataFrame(user_attributes_data, ["user_id", "role", "location"])

# Perform left join to enrich events with user attributes
enriched_df = events_df.join(user_attributes_df, on="user_id", how="left")

# Show the enriched DataFrame
enriched_df.show()
