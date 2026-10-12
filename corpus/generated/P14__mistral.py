import pandas as pd
from scipy.stats import norm

# Assuming df is your DataFrame with the following columns: 'customer_id', 'orders', 'refunds', 'average_order_value', 'purchase_frequency'

# Sample dataset for demonstration purposes
data = {
    'customer_id': range(1, 1001),
    'orders': range(1, 1001),
    'refunds': range(0, 999),
    'average_order_value': 100,
    'purchase_frequency': range(1, 10)
}

df = pd.DataFrame(data)

# Let's approximate retention rate by assuming it drops linearly over 5 periods
def calculate_retention_rate(n):
    dropout_rate = 0.1
    return 1 - (dropout_rate * n / 5)

# Calculate CLV using the formula: CLV = (average_order_value * purchase_frequency) / (1 - retention_rate)
def calculate_clv(customer):
    retention_rate = calculate_retention_rate(5)
    clv = (customer['average_order_value'] * customer['purchase_frequency']) / (1 - retention_rate)
    return clv

# Apply the function to each row in the DataFrame
df['customer_lifetime'] = df.apply(calculate_clv, axis=1)

# Print the first 10 rows of the DataFrame
print(df.head(10))
