import pandas as pd
from datetime import datetime

# Sample data creation
data = {
    'Date': ['2021-01-15', '2021-01-20', '2021-02-10', '2021-02-25', '2021-03-15', '2021-03-20'],
    'Product': ['Electronics', 'Clothing', 'Electronics', 'Clothing', 'Electronics', 'Clothing'],
    'Revenue': [1500, 800, 2000, 1200, 1800, 1000]
}

# Convert 'Date' column to datetime
df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'])

# Create a pivot table
pivot_table = df.pivot_table(values='Revenue', index=df['Date'].dt.to_period('M'), columns='Product', aggfunc='sum')

# Save the pivot table as an Excel report
pivot_table.to_excel('monthly_revenue_report.xlsx')

print("Excel report generated successfully.")
