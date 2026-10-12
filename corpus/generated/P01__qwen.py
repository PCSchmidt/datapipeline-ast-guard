import pandas as pd
import os

# Define the folder path where the CSV files are stored
folder_path = 'path/to/your/csv/folder'

# Define the output Parquet file path
output_path = 'path/to/your/output.parquet'

# Initialize an empty DataFrame to store the total revenue per region per day
total_revenue = pd.DataFrame(columns=['Region', 'Date', 'Revenue'])

# Iterate over all the files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)
        
        # Read the CSV file into a DataFrame
        sales_data = pd.read_csv(file_path)
        
        # Calculate the total revenue per day per region
        daily_revenue = sales_data.groupby(['Region', 'Date'])['Revenue'].sum().reset_index()
        
        # Append the result to the total_revenue DataFrame
        total_revenue = pd.concat([total_revenue, daily_revenue], ignore_index=True)

# Write the result to a Parquet file
total_revenue.to_parquet(output_path, index=False)
