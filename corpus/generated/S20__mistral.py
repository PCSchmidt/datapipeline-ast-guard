from pyspark.sql import SparkSession, functions as F
from google.cloud import storage

# Initialize SparkSession
spark = SparkSession.builder \
    .appName('LastMonthDataProcessing') \
    .getOrCreate()

# Google Cloud Storage credentials setup
storage_client = storage.Client()
bucket = storage_client.get_bucket('source-bucket')
blob = bucket.get_blob('path/to/your/parquet/file')

# Read data from Parquet file
df = spark.read.format('parquet').option('header', 'true').load(blob.generate_signed_url(expiration=3600, method='GET'))

# Filter data for last month (assuming data is timestamp-based)
current_year = F.year(F.current_timestamp())
current_month = F.month(F.current_timestamp())
last_month = F.when(F.month(F.current_timestamp()) == 1, (current_year - 1) * 12 + 12) \
             .when(F.month(F.current_timestamp()) == 12, current_year * 12 - 1) \
             .otherwise(current_year * 12 + 11 - F.month(F.current_timestamp()))

df = df.filter(F.month(df['timestamp_column']).isin([last_month]))

# Write filtered data to another bucket
destination_bucket = storage_client.get_bucket('destination-bucket')
output_path = 'path/to/destination/parquet/file'

df.write.format('parquet').save(output_path, mode='overwrite', storageOptions={
    'gsBucket': destination_bucket.name
})

# Close SparkSession
spark.stop()
