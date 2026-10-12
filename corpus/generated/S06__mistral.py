from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, MapType

# Create a SparkSession
spark = SparkSession.builder \
    .appName("JSON Log Analysis") \
    .config("spark.some.config.option", "some-value") \
    .getOrCreate()

# Define the JSON schema
json_schema = StructType(\
    [StructField("service", StringType()), \
     StructField("timestamp", StringType()), \
     StructField("data", MapType(StringType(), ArrayType(MapType(StringType(), StringType()))))])

# Read the JSON files and infer the schema
df = spark.read.option("multiline", "true").json("path/to/your/json/*.json", schema=json_schema)

# Extract service, timestamp, and error fields
df = df.withColumn("service", F.col("data.service")) \
      .withColumn("timestamp", F.from_unixtime(F.unix_timestamp(F.split(":", F.col("timestamp"))[1], "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'").cast(IntegerType()))) \
      .withColumn("error", F.col("data.error")) \
      .drop("data")

# Flatten the error field
df = df.withColumn("error", F.get_json_object(F.col("error"), "error")) \
      .withColumn("error_message", F.get_json_object(F.col("error"), "$.message")) \
      .withColumn("error_code", F.get_json_object(F.col("error"), "$.code")) \
      .drop("error")

# Group by service, hour, and error_code to count errors per service per hour
result = df.groupBy("service", F.hour(F.col("timestamp")).alias("hour")) \
           .agg(F.count("*").alias("error_count")) \
           .orderBy(F.col("service"), F.col("hour"))

# Show the results
result.show()
