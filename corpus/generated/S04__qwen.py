from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, count, sum, lit, round, concat_ws

# Initialize Spark session
spark = SparkSession.builder.appName("FunnelReport").getOrCreate()

# Sample data for demonstration
data = [
    ("Campaign A", "Visit", 1000),
    ("Campaign B", "Visit", 1500),
    ("Campaign A", "AddToCart", 300),
    ("Campaign B", "AddToCart", 450),
    ("Campaign A", "Purchase", 200),
    ("Campaign B", "Purchase", 300),
    ("Campaign A", "Visit", 200),
    ("Campaign B", "Visit", 500),
    ("Campaign A", "AddToCart", 50),
    ("Campaign B", "AddToCart", 100),
    ("Campaign A", "Purchase", 30),
    ("Campaign B", "Purchase", 40)
]

# Create DataFrame
df = spark.createDataFrame(data, ["Campaign", "Action", "Count"])

# Pivot the DataFrame to get counts for each action per campaign
pivot_df = df.groupBy("Campaign").pivot("Action").sum("Count").fillna(0)

# Calculate conversion rates
conversion_rates = pivot_df.withColumn(
    "ConversionRate",
    round((col("Purchase") / col("Visit")) * 100, 2)
)

# Calculate total visits, add-to-cart, and purchase counts
total_visits = pivot_df.agg(sum("Visit")).collect()[0][0]
total_add_to_cart = pivot_df.agg(sum("AddToCart")).collect()[0][0]
total_purchase = pivot_df.agg(sum("Purchase")).collect()[0][0]

# Add total counts to the conversion rates DataFrame
final_df = conversion_rates.withColumn(
    "TotalVisits", lit(total_visits)
).withColumn(
    "TotalAddToCart", lit(total_add_to_cart)
).withColumn(
    "TotalPurchase", lit(total_purchase)
)

# Reorder columns for better readability
final_df = final_df.select(
    "Campaign",
    "Visit",
    "AddToCart",
    "Purchase",
    "ConversionRate",
    "TotalVisits",
    "TotalAddToCart",
    "TotalPurchase"
)

# Show the funnel report
final_df.show()
