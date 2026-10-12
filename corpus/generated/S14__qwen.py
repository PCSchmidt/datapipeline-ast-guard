from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

# Initialize Spark session
spark = SparkSession.builder.appName("FileValidation").getOrCreate()

# Define the schema for validation
schema = "id INT, name STRING, age INT"

# Read the incoming file into a DataFrame
df = spark.read.format("csv").option("header", "true").option("inferSchema", "false").schema(schema).load("path/to/incoming/file")

# Define the validation rules
validation_rules = [
    (col("id").isNotNull(), "id cannot be null"),
    (col("name").isNotNull(), "name cannot be null"),
    (col("age") >= 0, "age must be non-negative")
]

# Apply validation rules and mark failed rows
for rule, error_message in validation_rules:
    df = df.withColumn("is_valid", when(rule, True).otherwise(False))

# Quarantine rows that fail validation
quarantine_df = df.filter(col("is_valid") == False)

# Save the quarantine DataFrame to a new file
quarantine_df.write.format("csv").option("header", "true").save("path/to/quarantine/file")

# Show the first 5 rows of the valid DataFrame
df.filter(col("is_valid") == True).show(5)

# Stop the Spark session
spark.stop()
