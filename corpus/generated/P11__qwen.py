import pandas as pd
from datetime import datetime

# Sample data creation
data = {
    'ProductLine': ['Electronics', 'Clothing', 'Electronics', 'Clothing', 'Electronics'],
    'Month': ['Jan', 'Jan', 'Feb', 'Feb', 'Mar'],
    'Revenue': [1000, 500, 1500, 1000, 2000]
}

# Creating DataFrame
df = pd.DataFrame(data)

# Converting 'Month' to datetime format if necessary
df['Month'] = pd.to_datetime(df['Month'], format='%b')

# Creating the pivot table
pivot_table = df.pivot_table(values='Revenue', index='Month', columns='ProductLine', aggfunc='sum')

# Save the pivot table to an Excel file
pivot_table.to_excel('monthly_revenue_report.xlsx')

# Display the pivot table
print(pivot_table)
