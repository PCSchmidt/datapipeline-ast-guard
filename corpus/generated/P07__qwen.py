import pandas as pd
from scipy.stats import zscore

# Load the sales data
# Assuming the data is in a CSV file named 'sales_data.csv' with columns 'store_id', 'sale_date', and 'sales_amount'
df = pd.read_csv('sales_data.csv')

# Convert 'sale_date' to datetime
df['sale_date'] = pd.to_datetime(df['sale_date'])

# Group by store and calculate the z-score of sales
df['z_score'] = df.groupby('store_id')['sales_amount'].transform(lambda x: (x - x.mean()) / x.std())

# Define a threshold for what is considered 'unusual'
threshold = 3

# Identify unusually high and low sales days
df['unusual_high'] = df['z_score'].abs() > threshold
df['unusual_low'] = df['z_score'] < -threshold

# Print the result
print(df[['store_id', 'sale_date', 'sales_amount', 'z_score', 'unusual_high', 'unusual_low']])
