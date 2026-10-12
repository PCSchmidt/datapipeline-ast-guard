from pyspark.sql import SparkSession
from pyspark.sql.functions import col, mean, stddev

# Initialize Spark session
spark = SparkSession.builder.appName("Anomaly Detection").getOrCreate()

# Sample data: store_id, date, sales_volume
data = [("Store1", "2021-01-01", 100), ("Store1", "2021-01-02", 120), ("Store1", "2021-01-03", 200),
        ("Store2", "2021-01-01", 50), ("Store2", "2021-01-02", 80), ("Store2", "2021-01-03", 150)]

# Create DataFrame
df = spark.createDataFrame(data, ["store_id", "date", "sales_volume"])

# Group by store_id and calculate mean and stddev of sales_volume
mean_stddev_df = df.groupBy("store_id").agg(mean("sales_volume").alias("mean_sales"), stddev("sales_volume").alias("stddev_sales"))

# Join the original data with the mean and stddev data
joined_df = df.join(mean_stddev_df, on="store_id", how="inner")

# Calculate the number of standard deviations from the mean
joined_df = joined_df.withColumn("sales_volume_anomaly", (col("sales_volume") - col("mean_sales")) / col("stddev_sales"))

# Filter the days where sales_volume is more than three standard deviations away from the mean
anomalies_df = joined_df.filter(abs(col("sales_volume_anomaly")) > 3)

# Select the store_id, date, and sales_volume
anomalies_df = anomalies_df.select("store_id", "date", "sales_volume")

# Show the anomalies
anomalies_df.show()

# Stop the Spark session
spark.stop()
