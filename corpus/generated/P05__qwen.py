import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, unix_timestamp, hour, count, when

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Log Analysis") \
    .getOrCreate()

# Sample JSON logs
json_logs = '''
[
    {"timestamp": "2023-04-01 10:00:00", "service": "service1", "level": "INFO", "message": "Log message"},
    {"timestamp": "2023-04-01 10:00:01", "service": "service2", "level": "ERROR", "message": "Error message"},
    {"timestamp": "2023-04-01 10:01:00", "service": "service1", "level": "ERROR", "message": "Another error"},
    {"timestamp": "2023-04-01 11:00:00", "service": "service2", "level": "INFO", "message": "Another log message"}
]
'''

# Load JSON data into DataFrame
df = spark.read.json(spark.sparkContext.parallelize([json_logs]))

# Flatten nested fields and count errors per service per hour
df_flattened = df.select(
    to_timestamp(col('timestamp'), 'yyyy-MM-dd HH:mm:ss').alias('timestamp'),
    col('service'),
    col('level'),
    col('message')
)

df_errors = df_flattened.filter(col('level') == 'ERROR')
df_counted = df_errors.groupBy(hour('timestamp'), 'service').agg(count('level').alias('error_count'))

# Show the result
df_counted.show()
