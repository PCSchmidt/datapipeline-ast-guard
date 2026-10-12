from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, current_timestamp

# Initialize Spark session
spark = SparkSession.builder \
    .appName("SCD Type 2 Update") \
    .getOrCreate()

# Load source data (change-data-capture updates)
cdf = spark.read.format("csv") \
    .option("header", "true") \
    .load("path_to_cdf_updates.csv")

# Load existing customer dimension table
customer_dim = spark.read.format("parquet") \
    .load("path_to_customer_dim")

# Apply SCD Type 2 logic
# Step 1: Mark end_date for existing rows where current record is an update
customer_dim = customer_dim.withColumn(
    "end_date",
    when(
        (col("customer_id").isin(cdf.select("customer_id").distinct().collect())) & 
        (col("end_date").isNull() | col("end_date") == current_timestamp()),
        current_timestamp()
    ).otherwise(col("end_date"))
)

# Step 2: Insert new rows for updated records
new_records = cdf.join(customer_dim, on="customer_id", how="left_anti")
customer_dim = customer_dim.union(new_records.withColumn("start_date", current_timestamp()).withColumn("end_date", None))

# Step 3: Write updated customer dimension table back to storage
customer_dim.write.mode("overwrite").format("parquet").save("path_to_customer_dim")

# Stop Spark session
spark.stop()
