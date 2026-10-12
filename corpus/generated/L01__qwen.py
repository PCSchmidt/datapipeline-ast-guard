import os
import pandas as pd

# Define the folder path containing CSV files
folder_path = 'path/to/csv/files'

# Initialize an empty DataFrame to store the results
result_df = pd.DataFrame()

# Loop through all files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        # Compute revenue per region per day
        df['revenue_per_region_per_day'] = df['revenue'] / df['region'] / df['day']
        # Append the result to the result DataFrame
        result_df = pd.concat([result_df, df], ignore_index=True)

# Save the result as Parquet
result_df.to_parquet('path/to/save/revenue_per_region_per_day.parquet')
