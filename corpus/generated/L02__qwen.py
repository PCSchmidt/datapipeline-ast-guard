import polars as pl

# Sample data
customers = pl.DataFrame({
    "customer_id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Charlie", "David"]
})

orders = pl.DataFrame({
    "order_id": [101, 102, 103],
    "customer_id": [1, 2, 3],
    "order_date": ["2023-01-01", "2023-02-15", "2023-03-20"]
})

# Convert order_date to Date type
orders = orders.with_column(pl.col("order_date").cast(pl.Date))

# Get the current date
current_date = pl.date.today()

# Define the date 90 days ago
ninety_days_ago = current_date - pl.duration(days=90)

# Filter orders from the last 90 days
recent_orders = orders.filter(pl.col("order_date") >= ninety_days_ago)

# Join customers with recent orders
joined_df = customers.join(recent_orders, on="customer_id", how="left")

# Filter customers with no orders in the last 90 days
customers_no_orders = joined_df.filter(pl.col("order_id").is_null())

# Select only customer_id and name
result = customers_no_orders.select(["customer_id", "name"])

# Print the result
print(result)
