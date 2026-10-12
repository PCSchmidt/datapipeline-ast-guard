from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, when, coalesce, datediff, lit

# Create a SparkSession
spark = SparkSession.builder.appName("CLTV_Calculation").getOrCreate()

# Read the orders and refunds tables
orders_df = spark.read.option("header", "true").option("inferSchema", "true").csv("orders.csv")
refunds_df = spark.read.option("header", "true").option("inferSchema", "true").csv("refunds.csv")

# Join the orders and refunds tables on customer_id
joined_df = orders_df.join(refunds_df, on="customer_id", how="left_outer")

# Calculate the number of days between the first order and last order (or refund)
first_order_date = col("order_date").first()
last_order_or_refund_date = col("order_date").last()
days_since_first_order = datediff(first_order_date, col("order_date"))

# Calculate the total spending per customer
total_spending = col("order_amount").sum() - col("refund_amount").first()

# Calculate the average order value (AOV) for each customer
aov = total_spending / days_since_first_order

# Calculate the customer lifetime value (CLTV) as the average order value multiplied by the number of days since the first order
cltv = aov * days_since_first_order

# Select only the customer_id and CLTV columns
result_df = joined_df.select(col("customer_id"), cltv.alias("CLTV"))

# Save the result to a CSV file
result_df.orderBy(col("CLTV").desc()).coalesce(1).write.option("header", "true").csv("cltv.csv")
