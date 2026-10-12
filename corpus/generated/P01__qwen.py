import pandas as pd
import os

# Define the folder path where the CSV files are located
folder_path = 'path/to/sales/folder'

# Initialize an empty DataFrame to store the total revenue per region per day
total_revenue = pd.DataFrame(columns=['Region', 'Date', 'Total_Revenue'])

# Loop through each file in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        # Read the CSV file into a DataFrame
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)
        
        # Calculate the total revenue for the current file
        df['Total_Revenue'] = df['Quantity'] * df['Price']
        
        # Append the result to the total_revenue DataFrame
        total_revenue = pd.concat([total_revenue, df], ignore_index=True)

# Group the total revenue by region and date
total_revenue = total_revenue.groupby(['Region', 'Date'], as_index=False)['Total_Revenue'].sum()

# Write the result to a Parquet file
output_file_path = 'path/to/output/total_revenue.parquet'
total_revenue.to_parquet(output_file_path, engine='pyarrow')

print(f"Total revenue per region per day has been written to {output_file_path}")
