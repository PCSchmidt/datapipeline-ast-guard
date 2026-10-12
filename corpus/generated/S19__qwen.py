from pyspark.sql import SparkSession
from pyspark.sql.functions import col, month, year, sum, when

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Monthly Recurring Revenue by Plan") \
    .getOrCreate()

# Load data
users = spark.read.parquet("path/to/users")
subscriptions = spark.read.parquet("path/to/subscriptions")
invoices = spark.read.parquet("path/to/invoices")

# Join tables
joined_df = users.join(subscriptions, users.user_id == subscriptions.user_id, "inner") \
    .join(invoices, subscriptions.subscription_id == invoices.subscription_id, "inner")

# Filter invoices to only include successful payments
joined_df = joined_df.filter(col("invoice_status") == "success")

# Compute monthly recurring revenue by plan
mrr_df = joined_df.groupBy(month("invoice_date"), year("invoice_date"), "plan") \
    .agg(sum(col("invoice_amount")).alias("monthly_revenue")) \
    .orderBy("year", "month", "plan")

# Show result
mrr_df.show()
