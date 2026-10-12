from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, from_unixtime, to_utc_timestamp

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Transaction USD Conversion") \
    .getOrCreate()

# Sample data for transactions
transactions = spark.createDataFrame([
    (1, "2023-01-01", 100, "EUR"),
    (2, "2023-01-02", 200, "GBP"),
    (3, "2023-01-03", 300, "JPY")
], ["id", "transaction_date", "amount", "currency"])

# Sample data for currency exchange rates
exchange_rates = spark.createDataFrame([
    ("2023-01-01", "EUR", 1.10),
    ("2023-01-02", "GBP", 1.30),
    ("2023-01-03", "JPY", 0.007)
], ["date", "currency", "rate"])

# Join transactions with exchange rates
converted_transactions = transactions.join(
    exchange_rates,
    (to_date(transactions.transaction_date) == exchange_rates.date) & (transactions.currency == exchange_rates.currency),
    "left"
)

# Calculate USD amount
converted_transactions = converted_transactions.withColumn(
    "usd_amount", col("amount") * col("rate")
)

# Select relevant columns
converted_transactions = converted_transactions.select("id", "transaction_date", "amount", "currency", "usd_amount")

# Show the result
converted_transactions.show()

# Stop the Spark session
spark.stop()
