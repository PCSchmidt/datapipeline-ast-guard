import pandas as pd

# Sample data for orders and refunds
orders_data = {
    'order_id': [101, 102, 103, 104, 105],
    'customer_id': [1, 2, 1, 3, 2],
    'order_date': ['2023-01-01', '2023-01-05', '2023-01-10', '2023-01-15', '2023-01-20'],
    'amount': [100, 200, 50, 300, 150]
}

refunds_data = {
    'refund_id': [1, 2],
    'order_id': [101, 104],
    'refund_date': ['2023-01-02', '2023-01-16'],
    'refund_amount': [50, 100]
}

# Create DataFrames
orders_df = pd.DataFrame(orders_data)
refunds_df = pd.DataFrame(refunds_data)

# Convert dates to datetime
orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
refunds_df['refund_date'] = pd.to_datetime(refunds_df['refund_date'])

# Calculate total order amount for each order
orders_df['total_order_amount'] = orders_df['amount']

# Merge refunds onto orders to subtract refunds
merged_df = pd.merge(orders_df, refunds_df, on='order_id', how='left', suffixes=('_order', '_refund'))

# Calculate net order amount by subtracting refunds
merged_df['net_order_amount'] = merged_df['total_order_amount'] - merged_df['refund_amount'].fillna(0)

# Group by customer and sum up net order amounts to get CLV
customer_clv = merged_df.groupby('customer_id')['net_order_amount'].sum().reset_index()
customer_clv.columns = ['customer_id', 'customer_lifetime_value']

print(customer_clv)
