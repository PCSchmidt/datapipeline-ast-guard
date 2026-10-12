from pyspark.sql import SparkSession, functions as F

# Create a SparkSession
spark = SparkSession.builder \
    .appName('DeduplicateEventLog') \
    .getOrCreate()

# Read the input CSV file
df = spark.read.csv("event_log.csv", header=True, inferSchema=True)

# Perform deduplication based on user_id and event_type
dedup_df = df.groupBy("user_id", "event_type").max() \
             .withColumnRenamed("max", "row")

# Join the original dataframe with the deduplicated dataframe to keep only the latest records per user_id and event_type
result_df = df.join(dedup_df, on=["user_id", "event_type", "timestamp"], how="left") \
              .where(F.col("row").isNotNull()) \
              .drop("row")

# Write the output to a new CSV file
result_df.write.csv("deduplicated_event_log.csv", mode="overwrite", header=True)

# Stop the SparkSession
spark.stop()
