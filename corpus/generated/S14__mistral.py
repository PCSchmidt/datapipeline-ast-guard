from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Schema Validation and Null Rates') \
    .getOrCreate()

# Define the schema for the CSV file
schema = StructType([
    StructField('column1', StringType(), True),
    StructField('column2', IntegerType(), True),
    StructField('column3', FloatType(), True),
    StructField('column4', DoubleType(), True)
])

# Read the CSV file and validate the schema
df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv("input/file.csv")

# Calculate null rates for each column
null_rates = df.stats().selectExpr("avg(isnull(column1))",
                                    "avg(isnull(column2))",
                                    "avg(isnull(column3))",
                                    "avg(isnull(column4))") \
    .collect()[0]

print("Null rates: ", null_rates)

# Write valid rows to the original location and invalid rows to a quarantine location
(df.filter(~F.col("column1").isNull() & ~F.col("column2").isNull() & ~F.col("column3").isNull() & ~F.col("column4").isNull())
    .write \
    .option("overwrite", "true") \
    .csv("input/file.csv")

invalid_df = df.filter(F.col("column1").isNull() | F.col("column2").isNull() | F.col("column3").isNull() | F.col("column4").isNull())

# Quarantine location (you should define the quarantine location path)
quarantine_location = "output/quarantine"

invalid_df.write \
    .option("overwrite", "true") \
    .csv(quarantine_location)
