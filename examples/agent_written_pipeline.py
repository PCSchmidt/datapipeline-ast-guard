"""A typical LLM-generated PySpark job. It passes a toy-data unit test and fails on a real cluster."""

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

orders = spark.read.parquet("s3://prod-data/orders/2026/")
customers = spark.read.csv("/data/customers.csv", header=True)

enriched = orders.join(customers)
regions = customers.crossJoin(orders.select("region"))

everything = enriched.collect()
preview = enriched.limit(100).toPandas()
