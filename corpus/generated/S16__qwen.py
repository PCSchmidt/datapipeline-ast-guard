from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, when

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Customer Lifetime Value Calculation") \
    .getOrCreate()

# Sample data for orders and refunds
data_orders = [
    (1, 100, "2023-01-01"),
    (2, 200, "2023-01-15"),
    (3, 150, "2023-02-01"),
    (1, 50, "2023-02-15"),
    (2, 75, "2023-03-01")
]

data_refunds = [
    (1, 50, "2023-02-01"),
    (2, 25, "2023-03-15"),
    (3, 75, "2023-04-01")
]

# Create DataFrames
orders_df = spark.createDataFrame(data_orders, ["customer_id", "amount", "order_date"])
refunds_df = spark.createDataFrame(data_refunds, ["customer_id", "amount", "refund_date"])

# Calculate net amount after refunds for each order
net_orders_df = orders_df.join(refunds_df, on="customer_id", how="left") \
    .withColumn("net_amount", col("amount") - when(col("refund_date").isNotNull(), col("amount")).otherwise(0)) \
    .groupBy("customer_id") \
    .agg(sum("net_amount").alias("total_net_amount"))

# Show the result
net_orders_df.show()

# Stop the Spark session
spark.stop()
