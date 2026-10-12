from pyspark.sql import SparkSession, functions as F

# Create a SparkSession
spark = SparkSession.builder \
    .appName('Rolling 7-day average') \
    .getOrCreate()

# Sample data
data = [("sensor1", 10.5, "2022-01-01"),
        ("sensor1", 11.0, "2022-01-02"),
        ("sensor1", 12.0, "2022-01-03"),
        ("sensor1", 13.0, "2022-01-04"),
        ("sensor1", 14.0, "2022-01-05"),
        ("sensor1", 15.0, "2022-01-06"),
        ("sensor1", 16.0, "2022-01-07"),

        ("sensor2", 20.5, "2022-01-02"),
        ("sensor2", 21.0, "2022-01-03"),
        ("sensor2", 22.0, "2022-01-04"),
        ("sensor2", 23.0, "2022-01-05"),
        ("sensor2", 24.0, "2022-01-06"),
        ("sensor2", 25.0, "2022-01-07")]

df = spark.createDataFrame(data, ["sensor", "reading", "date"])

# Define the Window specification
windowSpec = F.Window.partitionBy("sensor").orderBy(F.col("date")) \
    .rangeBetween(F.row_number().over(windowSpec) - 7, F.row_number().over(windowSpec))

# Compute the rolling 7-day average
df = df.withColumn("rolling_average", F.avg("reading").over(windowSpec))

# Show the results
df.show()
