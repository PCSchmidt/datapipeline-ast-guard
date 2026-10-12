import pandas as pd

# Load the data
data = pd.read_csv('revenue_data.csv')

# Parse the 'date' column as datetime
data['date'] = pd.to_datetime(data['date'])

# Pivot the data with monthly resolution
pivoted_data = data.pivot(index='date', columns='product_line', values='revenue')

# Reset the index and rename the columns
pivoted_data.reset_index(inplace=True)
pivoted_data.columns = ['date', 'product_line', 'monthly_revenue']

# Save the pivoted data back to a CSV file
pivoted_data.to_csv('pivoted_revenue_data.csv', index=False)
