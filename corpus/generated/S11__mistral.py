from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, TimestampType

today = F.current_date().format("yyyy-MM-dd")
yesterday = (F.current_date() - F.interval(1, 'day')).format("yyyy-MM-dd")

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("product_name", StringType(), True),
    StructField("created_at", TimestampType(), True)
])

yesterday_df = spark.sql("SELECT * FROM hive.products WHERE created_at = '{}'".format(yesterday))
today_df = spark.sql("SELECT * FROM hive.products WHERE created_at = '{}'".format(today))

# Create temporary views for easier querying
yesterday_df.createOrReplaceTempView("yesterday_view")
today_df.createOrReplaceTempView("today_view")

# Find new rows (today but not yesterday)
new_rows = spark.sql("SELECT * FROM today_view WHERE id NOT IN (SELECT id FROM yesterday_view)")

# Find removed rows (yesterday but not today)
removed_rows = spark.sql("SELECT * FROM yesterday_view WHERE id NOT IN (SELECT id FROM today_view)")

# Find changed rows (same id, but different product_name or different created_at)
changed_rows = spark.sql("""
    SELECT * FROM
    (
        SELECT
            yesterday_view.*,
            today_view.*
        FROM
            yesterday_view
            JOIN today_view ON yesterday_view.id = today_view.id
        WHERE
            yesterday_view.product_name != today_view.product_name
            OR yesterday_view.created_at != today_view.created_at
    )
    WHERE created_at IS NOT NULL
""")

# Report the results
new_rows.show()
removed_rows.show()
changed_rows.show()
