import pandas as pd

# Sample data
data = {
    'OrderID': [1, 2, 3, 4, 5],
    'CustomerID': [101, 102, 101, 103, 102],
    'OrderDate': ['2021-01-01', '2021-02-15', '2021-03-20', '2021-04-10', '2021-05-25'],
    'OrderAmount': [100, 150, 200, 50, 300],
    'RefundID': [None, None, None, 1, 2],
    'RefundDate': [None, None, None, '2021-04-20', '2021-06-01'],
    'RefundAmount': [None, None, None, 50, 100]
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert dates to datetime
df['OrderDate'] = pd.to_datetime(df['OrderDate'])
df['RefundDate'] = pd.to_datetime(df['RefundDate'])

# Calculate net order value by subtracting refunds
df['NetOrderValue'] = df['OrderAmount'] - df['RefundAmount']

# Calculate customer lifetime value
customer_lifetime_value = df.groupby('CustomerID')['NetOrderValue'].sum()

print(customer_lifetime_value)
