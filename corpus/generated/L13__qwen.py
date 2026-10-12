import pandas as pd

# Sample data: Orders and Refunds
data = {
    'order_id': [101, 102, 103, 104, 105],
    'customer_id': [1, 1, 2, 2, 3],
    'order_date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
    'amount': [100, 200, 150, 50, 300],
    'refund_id': [None, None, None, 104, None],
    'refund_date': [None, None, None, '2022-01-05', None],
    'refund_amount': [None, None, None, 50, None]
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert dates to datetime
df['order_date'] = pd.to_datetime(df['order_date'])
df['refund_date'] = pd.to_datetime(df['refund_date'])

# Calculate net amount for each order (subtract refund amount if applicable)
df['net_amount'] = df['amount'] - df['refund_amount']

# Calculate Customer Lifetime Value (CLV)
# Assuming a simple model where CLV is the sum of net amounts for each customer
customer_clv = df.groupby('customer_id')['net_amount'].sum().reset_index()
customer_clv.rename(columns={'net_amount': 'CLV'}, inplace=True)

print(customer_clv)
