import polars as pl

# Load the data from CSV, using Polars's FF format for faster loading
df = pl.read_csv("your_file.csv", format=pl.Format.CSV, chunk_size=1000000)

# Show the first few rows
print(df.head())

# Calculate basic statistics
stats = df.stat('mean', 'min', 'max', 'std', 'count').groupby([pl.col('column_name_1'), pl.col('column_name_2')])
print(stats)
