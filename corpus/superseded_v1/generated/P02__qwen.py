import pandas as pd
from datetime import datetime, timedelta

# Sample data creation
customers_data = {
    'CustomerID': [1, 2, 3, 4, 5],
    'CustomerName': ['John Doe', 'Jane Smith', 'Alice Johnson', 'Bob Brown', 'Charlie Davis']
}
orders_data = {
    'OrderID': [101, 102, 103, 104, 105],
    'CustomerID': [1, 2, 3, 4, 1],
    'OrderDate': ['2023-04-01', '2023-04-15', '2023-03-20', '2023-05-10', '2023-04-01']
}

# Convert data to pandas DataFrames
customers = pd.DataFrame(customers_data)
orders = pd.DataFrame(orders_data)

# Convert OrderDate to datetime
orders['OrderDate'] = pd.to_datetime(orders['OrderDate'])

# Find the current date and subtract 90 days
current_date = datetime.now()
threshold_date = current_date - timedelta(days=90)

# Filter orders to find customers who have not ordered in the last 90 days
inactive_customers = orders[orders['OrderDate'] < threshold_date]['CustomerID']

# Merge with customers to get customer names
inactive_customers_info = customers[customers['CustomerID'].isin(inactive_customers)]

print("Inactive Customers who have not ordered in the last 90 days:")
print(inactive_customers_info)
