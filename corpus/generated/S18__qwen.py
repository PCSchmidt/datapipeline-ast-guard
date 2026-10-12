from pyspark.sql import SparkSession
from pyspark.sql.functions import col, date_format, sum, avg, max, min, lit

# Initialize Spark session
spark = SparkSession.builder \
    .appName("Quarterly Report Generator") \
    .getOrCreate()

# Load data into DataFrame
df = spark.read.format("csv").option("header", "true").load("path_to_your_data.csv")

# Assuming the DataFrame has a 'date' column in the format 'yyyy-mm-dd'
df = df.withColumn("date", col("date").cast("date"))

# Extract quarter from the date
df = df.withColumn("quarter", date_format(col("date"), "yyyy-qq"))

# Aggregate data by quarter
report_df = df.groupBy("quarter") \
    .agg(
        sum(col("sales")).alias("total_sales"),
        avg(col("profit")).alias("average_profit"),
        max(col("revenue")).alias("max_revenue"),
        min(col("cost")).alias("min_cost")
    )

# Add a report title
report_df = report_df.withColumn("Report Title", lit("Quarterly Financial Report"))

# Add a timestamp
from pyspark.sql.functions import current_timestamp
report_df = report_df.withColumn("Report Generated On", current_timestamp())

# Save the report to a CSV file
report_df.write.format("csv").option("header", "true").save("path_to_save_report.csv")

# Stop the Spark session
spark.stop()
