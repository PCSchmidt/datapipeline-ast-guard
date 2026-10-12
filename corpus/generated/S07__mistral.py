from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Currency Exchange Rate Script') \
    .getOrCreate()

# Read transactions data
transactions = spark \
    .read \
    .option("header", "true") \
    .csv("hdfs://namenode/user/transactions.csv")

# Read currency exchange rate data
exchange_rates = spark \
    .read \
    .option("header", "true") \
    .csv("hdfs://namenode/user/exchange_rates.csv")

# Join the tables on date and currency
exchange_joined = exchange_rates \
    .join(transactions, on=["date", "currency"], how="inner")

# Add a column for converted amount in USD
exchange_joined = exchange_joined \
    .withColumn("converted_amount_usd", exchange_rates["rate"] * transactions["amount"])

# Show the result
exchange_joined.show()

# Save the result to a new CSV file in HDFS
exchange_joined.write \
    .option("header", "true") \
    .csv("hdfs://namenode/user/converted_transactions.csv")
