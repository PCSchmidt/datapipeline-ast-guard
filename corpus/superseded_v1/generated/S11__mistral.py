import pandas as pd
from dateutil.relativedelta import relativedelta

# Set paths to yesterday's and today's CSV files
yesterday_file = 'yesterday_products.csv'
today_file = 'today_products.csv'

# Read data from CSV files
yesterday_data = pd.read_csv(yesterday_file)
today_data = pd.read_csv(today_file)

# Ensure both DataFrames have the same column names
assert set(yesterday_data.columns) == set(today_data.columns), "Both DataFrames must have the same column names"

# Calculate the relative date difference to compare yesterday's data with today's data
yesterday = pd.to_datetime(yesterday_data['date_created'])
today = pd.to_datetime(today_data['date_created'])

# Find rows that were added
added_rows = today_data[~today_data['id'].isin(yesterday_data['id'])].reset_index(drop=True)

# Find rows that were removed
removed_rows = yesterday_data[~yesterday_data['id'].isin(today_data['id'])].reset_index(drop=True)

# Find rows that were changed (assuming that 'price' column is changed frequently)
changed_rows = pd.merge(yesterday_data, today_data, on='id')
changed_rows = changed_rows[~changed_rows.isin(['yesterday', 'today']).all(1)]
changed_rows['change'] = changed_rows.apply(lambda row: 'price' if row['yesterday'] != row['today'] else None, axis=1)
changed_rows = changed_rows[changed_rows['change'].notnull()]

# Print or save the results
print(f"Added rows:\n{added_rows}\n")
print(f"Removed rows:\n{removed_rows}\n")
print(f"Changed rows:\n{changed_rows[['id', 'change']]}\n")
