import pandas as pd
import numpy as np

# Assuming the data is already loaded into a DataFrame named 'quarterly_data'
# For demonstration, let's create a sample DataFrame
data = {
    'Category': ['Revenue', 'Expenses', 'Profit'],
    'Q1': [1000, 800, 200],
    'Q2': [1200, 900, 300],
    'Q3': [1300, 1000, 300],
    'Q4': [1400, 1100, 300]
}
quarterly_data = pd.DataFrame(data)

# Adding a column for the total per category
quarterly_data['Total'] = quarterly_data[['Q1', 'Q2', 'Q3', 'Q4']].sum(axis=1)

# Exporting the DataFrame to a CSV file
quarterly_data.to_csv('quarterly_report.csv', index=False)

print("Quarterly report CSV file has been created successfully.")
