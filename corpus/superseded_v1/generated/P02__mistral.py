import pandas as pd

def merge_and_find_no_orders_customers(orders_df, customers_df, order_date_column='order_date', customer_id_column='customer_id'):
    # Merge orders and customers dataframes
    merged_df = pd.merge(orders_df, customers_df, on='customer_id')

    # Convert order date to datetime
    merged_df[order_date_column] = pd.to_datetime(merged_df[order_date_column])

    # Calculate the number of days since the last order
    merged_df['days_since_last_order'] = (pd.to_datetime('today') - merged_df[order_date_column]).dt.days

    # Filter customers who have not ordered in the last 90 days
    no_orders_customers = merged_df[merged_df['days_since_last_order'] > 90]['customer_id'].unique()

    return no_orders_customers

# Sample data
orders_df = pd.DataFrame({
    'customer_id': [1, 1, 2, 2, 3],
    'order_date': ['2021-01-01', '2021-02-01', '2020-01-01', '2020-12-01', '2021-03-01']
})

customers_df = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'customer_name': ['John', 'Jane', 'Dave']
})

# Find customers who have not ordered in the last 90 days
no_orders_customers = merge_and_find_no_orders_customers(orders_df, customers_df)
print(no_orders_customers)
