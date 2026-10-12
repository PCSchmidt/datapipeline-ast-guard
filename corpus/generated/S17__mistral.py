from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType
from pyspark.sql.functions import unix_timestamp, to_date, when, lit

# Define the schema for the pivoted DataFrame
pivot_schema = StructType([
    StructField("date", DateType(), True),
    StructField(f"{product_line}", IntegerType(), True) for product_line in df.select(F.distinct(F.lower(F.split(F.lower(F.col("product_line")), "_"))[1])).collect()
])

# Pivot the DataFrame
pivot_df = df.groupBy(unix_timestamp(to_date(F.substring(F.col("date"), 6), "yyyy-MM-dd").cast("date")).cast("int")) \
             .pivot("product_line") \
             .agg(F.sum("revenue")) \
             .withColumnRenamed("sum(revenue)", "revenue") \
             .select(F.col("date"), *[F.col(f"{product_line}") for product_line in pivot_df.columns if "date" not in product_line]) \
             .withColumn("date", F.to_date(F.col("date"), "yyyyMM")) \
             .drop("date").withType(pivot_schema)

pivot_df.show()
