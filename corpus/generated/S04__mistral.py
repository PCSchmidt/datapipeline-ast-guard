from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Funnel Report') \
    .getOrCreate()

# Define the schema for the events DataFrame
events_schema = StructType([
    StructField('user_id', IntegerType(), True),
    StructField('timestamp', TimestampType(), True),
    StructField('campaign_id', IntegerType(), True),
    StructField('page_event', StringType(), True),
    StructField('event_type', StringType(), True)
])

# Load the events data
events = spark.read.format('csv') \
    .option('header', 'true') \
    .option('inferSchema', 'true') \
    .schema(events_schema) \
    .load('path/to/your/events.csv')

# Define the window function for the funnel stages
window_spec = F.Window.partitionBy('user_id', 'campaign_id') \
    .orderBy('timestamp')

# Create the funnel stages DataFrames
visits = events.filter(F.col('event_type') == 'visit')
add_to_cart = visits.withWatermark('timestamp', '1 hour') \
    .join(events.filter(F.col('event_type') == 'add_to_cart'),
          on=['user_id', 'campaign_id', F.col('timestamp').greaterThanOrEqualTo(visits['timestamp'])),
          how='left') \
    .filter(F.col('add_to_cart.event_type').isNull())

purchases = add_to_cart.withWatermark('timestamp', '1 day') \
    .join(events.filter(F.col('event_type') == 'purchase'),
          on=['user_id', 'campaign_id', F.col('timestamp').greaterThanOrEqualTo(add_to_cart['timestamp'])],
          how='left') \
    .filter(F.col('purchase.event_type').isNull())

# Calculate the conversion rate for each marketing campaign
campaign_conversion_rates = purchases.groupBy('campaign_id') \
    .agg(F.countDistinct('user_id').alias('total_users'),
         F.count('*').alias('total_purchases')) \
    .withColumn('conversion_rate', F.when(F.col('total_purchases') > 0, F.col('total_purchases') / F.col('total_users'), F.lit(0)))

# Join the funnel stages DataFrames and the conversion rate DataFrame
funnel_report = visits \
    .join(add_to_cart, on=['user_id', 'campaign_id', F.col('timestamp').greaterThanOrEqualTo(visits['timestamp'])),
          how='left') \
    .join(purchases, on=['user_id', 'campaign_id', F.col('timestamp').greaterThanOrEqualTo(add_to_cart['timestamp'])],
          how='left') \
    .join(campaign_conversion_rates, on='campaign_id')

# Show the funnel report DataFrame
funnel_report.show()

# Save the funnel report as a DataFrame
funnel_report.write.format('parquet').save('path/to/output/funnel_report.parquet')
