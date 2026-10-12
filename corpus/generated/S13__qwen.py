from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, rank
from pyspark.sql.window import Window

# Initialize Spark session
spark = SparkSession.builder.appName("TopProductsByRevenue").getOrCreate()

# Sample data: product ID, category, revenue
data = [
    (1, 'Electronics', 1500),
    (2, 'Electronics', 2000),
    (3, 'Clothing', 800),
    (4, 'Clothing', 1200),
    (5, 'Electronics', 1800),
    (6, 'Clothing', 1000),
    (7, 'Electronics', 2500),
    (8, 'Electronics', 3000),
    (9, 'Clothing', 1400),
    (10, 'Electronics', 2200)
]

# Create DataFrame
df = spark.createDataFrame(data, ["product_id", "category", "revenue"])

# Window specification to rank products within each category by revenue
window_spec = Window.partitionBy("category").orderBy(col("revenue").desc())

# Add rank column
df_with_rank = df.withColumn("rank", rank().over(window_spec))

# Filter to get top 10 products in each category
top_products = df_with_rank.filter(col("rank") <= 10).select("category", "product_id", "revenue")

# Show the result
top_products.show()

# Stop Spark session
spark.stop()
