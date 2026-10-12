import pandas as pd

# Read the CSV file
data = pd.read_csv('sales_data.csv')

# Assuming the CSV file has columns: 'month', 'product_line', 'revenue'
pivot_table = data.pivot_table(index='month', columns='product_line', values='revenue', aggfunc='sum')

# Save the pivot table to an Excel file
pivot_table.to_excel('pivot_table_monthly_revenue_by_product_line.xlsx')
