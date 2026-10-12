from pyspark.sql import SparkSession, functions as F, Window
from pyspark.sql.functions import unix_timestamp, col

# Create a SparkSession
spark = SparkSession.builder \
    .appName('JoinOrdersCustomers') \
    .getOrCreate()

# Assuming orders and customers tables are in parquet format in hdfs
orders_df = spark.read.format('parquet').option('hdfs.path', 'hdfs://your-hdfs-path/orders').load()
customers_df = spark.read.format('parquet').option('hdfs.path', 'hdfs://your-hdfs-path/customers').load()

# Join the orders and customers tables
joined_df = customers_df.join(orders_df, on='customer_id', how='inner')

# Create a window specification for the last 90 days
window = Window.orderBy(F.col('order_date').desc()) \
    .row_number().over(windowSpec=(windowSpecification, '90 days'))

# Filter out customers who have not placed an order in the last 90 days
no_orders_in_90_days = joined_df \
    .withColumn('order_date_ts', unix_timestamp(col('order_date'), 'yyyy-MM-dd').cast('timestamp')) \
    .withColumn('row_number', F.row_number().over(window)) \
    .filter(col('row_number') > 1) \
    .drop('order_date_ts', 'row_number')

# Save the result as a DataFrame named no_orders_in_90_days
no_orders_in_90_days.write.format('parquet').option('hdfs.path', 'hdfs://your-hdfs-path/no_orders_in_90_days').save()
