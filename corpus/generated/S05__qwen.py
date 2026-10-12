from pyspark.sql import SparkSession
from pyspark.sql.window import Window
from pyspark.sql.functions import avg

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Rolling Average Calculation") \
    .getOrCreate()

# Sample data
data = [
    ("sensor1", "2023-04-01", 10),
    ("sensor1", "2023-04-02", 15),
    ("sensor1", "2023-04-03", 20),
    ("sensor1", "2023-04-04", 25),
    ("sensor1", "2023-04-05", 30),
    ("sensor1", "2023-04-06", 35),
    ("sensor1", "2023-04-07", 40),
    ("sensor2", "2023-04-01", 12),
    ("sensor2", "2023-04-02", 17),
    ("sensor2", "2023-04-03", 22),
    ("sensor2", "2023-04-04", 27),
    ("sensor2", "2023-04-05", 32),
    ("sensor2", "2023-04-06", 37),
    ("sensor2", "2023-04-07", 42),
]

# Create DataFrame
df = spark.createDataFrame(data, ["sensor", "date", "reading"])

# Convert date column to date type
df = df.withColumn("date", df["date"].cast("date"))

# Define window specification
window_spec = Window.partitionBy("sensor").orderBy("date").rowsBetween(-6, 0)

# Calculate rolling 7-day average
df = df.withColumn("rolling_avg", avg("reading").over(window_spec))

# Show the result
df.show()

# Stop Spark session
spark.stop()
