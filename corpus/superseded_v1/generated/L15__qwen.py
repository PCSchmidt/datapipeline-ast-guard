import pandas as pd

# Replace 'large_table.csv' with the path to your large table file
file_path = 'large_table.csv'

# Read the first 1000 rows of the table
df = pd.read_csv(file_path, nrows=1000)

# Display the first few rows of the DataFrame
print("First few rows of the DataFrame:")
print(df.head())

# Display basic statistics of the DataFrame
print("\nBasic statistics of the DataFrame:")
print(df.describe(include='all'))
