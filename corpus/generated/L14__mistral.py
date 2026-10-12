import pandas as pd

# Assuming df is your DataFrame and it has columns 'Month', 'Year', 'Product Line', 'Revenue'
df = pd.DataFrame({
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'Year': [2021] * 12,  # Replace with your actual year data
    'Product Line': list('A B A A B A A B B A A B B'.upper()),  # Replace with your actual product line data
    'Revenue': [100, 120, 150, 130, 140, 160, 180, 170, 190, 200, 210, 220]  # Replace with your actual revenue data
})

# Ensure 'Month' and 'Year' are date-like and sort the dataframe
df['Month'] = pd.to_datetime(df['Month'], format='%b')
df.sort_values(by=['Year', 'Month'], inplace=True)

# Pivot the dataframe to transform each month into a column
monthly_revenue = df.pivot(index='Year', columns='Month', values='Revenue')
monthly_revenue = monthly_revenue.reset_index()

# Rename the columns for clarity
monthly_revenue.columns = ['Year', 'Month', 'Revenue_' + month.strftime('%b') for month in monthly_revenue['Month'].unique()]
monthly_revenue = monthly_revenue[['Year'] + [c for c in monthly_revenue.columns if c.startswith('Revenue_')]]

# Group by product line and sum the revenue per month
pivot_df = monthly_revenue.melt(id_vars='Year', var_name='Product Line', value_name='Revenue')
pivot_df = pivot_df.groupby(['Year', 'Product Line'])['Revenue'].sum().reset_index()

print(pivot_df)
