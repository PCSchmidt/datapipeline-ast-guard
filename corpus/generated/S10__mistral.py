from pyspark.sql import SparkSession, functions as F
from pyspark.sql.functions import col, lit
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType
from kafka import KafkaConsumer

# Create a SparkSession
spark = SparkSession.builder \
    .appName('CDC-SCD2') \
    .getOrCreate()

# Define the customer dimension schema
customer_schema = StructType([
    StructField('customer_id', IntegerType(), True),
    StructField('name', StringType(), True),
    StructField('update_ts', TimestampType(), True),
    StructField('is_deleted', IntegerType(), True)
])

# Read the customer dimension table
customer_table = spark.read.format('parquet').schema(customer_schema).load('path/to/customer_dimension')

# Create a Kafka consumer for the CDC updates
consumer = KafkaConsumer('your_cdc_topic',
                          bootstrap_servers='your_kafka_server',
                          value_deserializer=lambda m: bytearray(m.decode('utf-8')),
                          group_id='cdc-group')

# Process CDC updates and apply Type 2 SCD
def process_cdc_updates(df, cdc_df):
    # Merge CDC updates with the customer table
    merged_df = df.merge(cdc_df, on='customer_id', how='outer')

    # When the record is being inserted or updated, create a new row with the current timestamp
    merged_df = merged_df.withColumn('is_deleted', F.when(col('is_deleted').isNull(), 0).otherwise(1))
    merged_df = merged_df.withColumn('update_ts', F.when(col('is_deleted').isNull(), F.current_timestamp()).otherwise(col('update_ts')))
    merged_df = merged_df.withColumn('is_deleted', F.when(col('is_deleted') == 0, 0).otherwise(1))

    # Write the updated customer table to a Parquet file
    merged_df.write.format('parquet').save('path/to/customer_dimension')

# Process CDC updates and apply Type 2 SCD
process_cdc_updates(customer_table, spark.createDataFrame([], customer_schema))

# Process CDC updates from Kafka
for message in consumer:
    cdc_df = spark.createDataFrame([message.value], customer_schema)
    process_cdc_updates(customer_table, cdc_df)
