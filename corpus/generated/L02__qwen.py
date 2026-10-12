import pandas as pd

# Assuming 'orders' and 'customers' are your dataframes
# orders = pd.read_csv('orders.csv')
# customers = pd.read_csv('customers.csv')

# Convert 'order_date' to datetime
orders['order_date'] = pd.to_datetime(orders['order_date'])

# Filter orders from the last 90 days
recent_orders = orders[orders['order_date'] >= orders['order_date'].max() - pd.Timedelta(days=90)]

# Find customers with no recent orders
customers_with_no_orders = customers[~customers['customer_id'].isin(recent_orders['customer_id'])]

# Print the result
print(customers_with_no_orders)
