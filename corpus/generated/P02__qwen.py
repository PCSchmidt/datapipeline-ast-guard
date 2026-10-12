import pandas as pd
from datetime import datetime, timedelta

# Sample data creation
# Customer data
customers = pd.DataFrame({
    'customer_id': [101, 102, 103, 104],
    'customer_name': ['Alice', 'Bob', 'Charlie', 'David']
})

# Order data
orders = pd.DataFrame({
    'order_id': [1, 2, 3, 4],
    'customer_id': [101, 102, 101, 103],
    'order_date': pd.to_datetime(['2023-01-01', '2023-02-15', '2023-03-10', '2023-04-05'])
})

# Calculate the current date
current_date = datetime.now()

# Find the date 90 days ago
cutoff_date = current_date - timedelta(days=90)

# Merge orders with customers
merged_data = pd.merge(orders, customers, on='customer_id')

# Filter customers who have not ordered in the last 90 days
inactive_customers = merged_data[merged_data['order_date'] < cutoff_date]['customer_id'].drop_duplicates()

# Get the details of inactive customers
inactive_customers_details = customers[customers['customer_id'].isin(inactive_customers)]

print("Customers who have not ordered in the last 90 days:")
print(inactive_customers_details)
