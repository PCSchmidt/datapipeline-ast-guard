import pandas as pd

# Sample data for orders and customers tables
orders_data = {
    'order_id': [1, 2, 3, 4, 5],
    'customer_id': [101, 102, 103, 101, 104],
    'order_date': ['2021-01-01', '2021-02-15', '2021-03-20', '2021-04-10', '2021-05-05']
}

customers_data = {
    'customer_id': [101, 102, 103, 104, 105],
    'customer_name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
}

# Create DataFrames
orders_df = pd.DataFrame(orders_data)
customers_df = pd.DataFrame(customers_data)

# Convert order_date to datetime
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])

# Find customers who have not placed an order in the last 90 days
current_date = pd.Timestamp.now()
last_90_days = current_date - pd.Timedelta(days=90)
customers_without_orders = customers_df[~customers_df['customer_id'].isin(orders_df[orders_df['order_date'] > last_90_days]['customer_id'])]

print(customers_without_orders)
