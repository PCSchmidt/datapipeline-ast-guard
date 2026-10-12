import polars as pl

# Sample data for orders and customers
orders = pl.DataFrame({
    "customer_id": [1, 2, 3, 4, 5, 6],
    "order_date": pl.Date(['2022-01-01', '2022-01-02', '2022-01-03', '2021-12-31', '2022-01-04', '2022-01-05'])
})

customers = pl.DataFrame({
    "customer_id": [1, 2, 3, 4, 5, 6, 7],
    "customer_name": ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace']
})

# Join the orders and customers tables
joined = orders.join(customers, on='customer_id', how='outer')

# Filter for customers without any orders in the last 90 days
last_90_days = pl.LocalDateTime.now().shift(-90).date()
no_orders_in_90_days = joined.filter(pl.col('order_date').is_null() | (joined['order_date'] <= last_90_days)).drop('order_date')

# Show the customers with no orders in the last 90 days
no_orders_in_90_days.select(['customer_id', 'customer_name']).show()
