from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date, datediff

# Initialize Spark session
spark = SparkSession.builder.appName("CustomerOrderAnalysis").getOrCreate()

# Sample data for orders and customers
orders_data = [
    (1, 1, '2022-01-15'),
    (2, 2, '2022-02-20'),
    (3, 1, '2022-03-10'),
    (4, 3, '2022-04-05'),
    (5, 2, '2022-05-12')
]

customers_data = [
    (1, 'John Doe'),
    (2, 'Jane Smith'),
    (3, 'Alice Johnson')
]

# Create DataFrame for orders and customers
orders_df = spark.createDataFrame(orders_data, ['order_id', 'customer_id', 'order_date'])
customers_df = spark.createDataFrame(customers_data, ['customer_id', 'customer_name'])

# Join orders and customers on customer_id
joined_df = orders_df.join(customers_df, on='customer_id', how='left')

# Filter customers who have not placed an order in the last 90 days
result_df = joined_df.filter(datediff(current_date(), 'order_date') > 90).select('customer_id', 'customer_name')

# Show the result
result_df.show()

# Stop the Spark session
spark.stop()
