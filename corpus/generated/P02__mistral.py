import pandas as pd

# Assuming you have two CSV files: customers.csv and orders.csv
customers_df = pd.read_csv('customers.csv')
orders_df = pd.read_csv('orders.csv')

# Merge the customers and orders dataframes
merged_df = pd.merge(customers_df, orders_df, on='customer_id')

# Filter out orders within the last 90 days
today = pd.Timestamp('today')
last_90_days = today - pd.Timedelta(days=90)
filtered_df = merged_df[merged_df['order_date'] < last_90_days]

# Find customers who have not ordered in the last 90 days
no_orders_customers = filtered_df.groupby('customer_id').filter(lambda x: len(x) == 0)

# Display the customers who have not ordered in the last 90 days
print(no_orders_customers[['customer_id', 'customer_name']])
