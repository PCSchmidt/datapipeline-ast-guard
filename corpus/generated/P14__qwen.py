import pandas as pd

# Sample data
data = {
    'customer_id': [1, 1, 2, 2, 3],
    'order_id': [101, 102, 201, 202, 301],
    'order_date': ['2023-01-01', '2023-01-10', '2023-02-01', '2023-02-15', '2023-03-01'],
    'amount': [100, 150, 200, 50, 250],
    'is_refund': [False, False, False, True, False]
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert order_date to datetime
df['order_date'] = pd.to_datetime(df['order_date'])

# Calculate total revenue
df['revenue'] = df['amount'] * (1 - df['is_refund'].astype(int))

# Calculate customer lifetime value (CLV)
# Assuming a discount rate of 10% per year and a customer lifetime of 3 years
df['CLV'] = df.groupby('customer_id')['revenue'].sum() / 0.9 ** (df.groupby('customer_id')['order_date'].max() - df['order_date']).dt.days / 365 * 3

# Display the result
print(df[['customer_id', 'CLV']].drop_duplicates())
