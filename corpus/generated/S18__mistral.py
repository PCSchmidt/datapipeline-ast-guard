from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Quarterly Report Generator') \
    .config('spark.some.config.option', 'some-value') \
    .getOrCreate()

# Assuming df is your DataFrame
quarter_mapping = {1: 'Q1', 2: 'Q2', 3: 'Q3', 4: 'Q4'}

# Create a new DataFrame with the quarter column
df = df.withColumn('Quarter', when((col('month') <= 3) & (col('year') % 4 != 0) | (col('month') > 3) & (col('month') <= 6) & (col('year') % 4 == 0) | (col('month') > 6) & (col('month') <= 9) & (col('year') % 4 != 0) | (col('month') > 9) & (col('month') <= 12) & (col('year') % 4 == 0), lit(quarter_mapping[col('month')]))
                                                                 .whenOtherwise(lit('Invalid Quarter')))

# Drop the month and year columns
df = df.drop('month', 'year')

# Save the DataFrame as a CSV file
df.coalesce(1).write.format('csv').save('quarterly_report.csv', mode='overwrite')

# Stop the SparkSession
spark.stop()
