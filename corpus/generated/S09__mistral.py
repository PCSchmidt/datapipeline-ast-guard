from pyspark.sql import functions as F, SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Sessionize Clickstream') \
    .getOrCreate()

# Define the schema for clickstream data
clickstream_schema = StructType([
    StructField('user_id', IntegerType(), True),
    StructField('timestamp', TimestampType(), True),
    StructField('event', StringType(), True)
])

# Read input data (assuming it's a CSV file)
clickstream_df = spark.read.format('csv') \
    .schema(clickstream_schema) \
    .option('header', 'true') \
    .load('input_data.csv')

# Create a window specification for the sessionization
session_window = F.window(F.col('timestamp'), '30 minutes', '1 minute')

# Define a UDF to create a new session ID for each user
def create_session_id(user_id, start_time):
    return f'{user_id}_{start_time.toString("yyyy-MM-dd_HH:mm:ss")}'

create_session_id_udf = F.udf(create_session_id, StringType())

# Sessionize the data and create a new session column
sessionized_df = clickstream_df \
    .withColumn('session_id', create_session_id_udf(F.col('user_id'), F.first('timestamp').over(session_window))) \
    .withWatermark('timestamp', '30 minutes') \
    .groupBy('session_id') \
    .agg(F.max('timestamp').alias('end_time'), F.first('user_id').alias('user_id'), F.collect_list('event').alias('events')) \
    .withColumn('duration', F.datediff('end_time', F.first('timestamp')) * F.interval('1 minute', 'minute')) \
    .drop('end_time')

# Save the sessionized data to a new CSV file
sessionized_df.write.format('csv') \
    .option('header', 'true') \
    .save('output_data.csv')
