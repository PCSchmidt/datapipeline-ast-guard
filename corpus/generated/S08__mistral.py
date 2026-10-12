from pyspark.sql import functions as F
from pyspark.sql.functions import col

# Assuming df is your DataFrame with columns 'store_id', 'day', and 'sales_volume'
anomaly_df = df \
    .groupBy('store_id') \
    .agg(F.avg('sales_volume').alias('mean'),
         F.stddev('sales_volume').alias('stddev')) \
    .withColumn('anomaly_threshold', col('mean') + (3 * col('stddev'))) \
    .withColumn('is_anomaly', col('sales_volume') > col('anomaly_threshold')) \
    .select('store_id', 'day', 'sales_volume', 'is_anomaly')

anomaly_df.show()
