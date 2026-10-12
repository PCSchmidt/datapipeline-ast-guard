import polars as pl

# Load the data from a CSV file
df = pl.read_csv("path_to_your_large_table.csv")

# Display the first few rows of the DataFrame
print("First few rows of the DataFrame:")
print(df.head())

# Display basic statistics of the DataFrame
print("\nBasic statistics of the DataFrame:")
print(df.describe())
