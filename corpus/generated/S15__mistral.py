from pyspark.sql import functions as F, SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, LongType
from pyspark.sql.streaming import StreamingDataSet

# Define the schema for the events and lookup table
events_schema = StructType([
    StructField("event_id", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("timestamp", LongType(), True)
])

lookup_schema = StructType([
    StructField("key", IntegerType(), True),
    StructField("value", StringType(), True)
])

# Create a SparkSession
spark = SparkSession.builder \
    .appName("EventEnrichment") \
    .getOrCreate()

# Read events stream
events_stream = spark \
    .readStream \
    .format("csv") \
    .option("header", "true") \
    .schema(events_schema) \
    .load("events.csv")

# Read lookup table
lookup_table = spark \
    .createDataFrame([(1, "attribute1"), (2, "attribute2"), (3, "attribute3")], lookup_schema)

# Join events with lookup table
enriched_events = events_stream \
    .join(lookup_table, on="event_id", how="left") \
    .withColumn("enriched_value", F.when(F.col("event_id").isin(F.collect(lookup_table.select("key"))), F.col("value")) \
                                   .otherwise(F.lit("")))

# Write the enriched events to a console sink
query = enriched_events \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

# Start the query and print the query ID
query_id = query.id
print(f"Enriched events query started with ID: {query_id}")

# Run the script indefinitely
spark.streams.awaitAnyTermination()
