import polars as pl

# Sample data
data = {
    'product_line': ['A', 'B', 'A', 'C', 'B', 'C'],
    'month': ['Jan', 'Jan', 'Feb', 'Feb', 'Feb', 'Jan'],
    'revenue': [100, 200, 150, 300, 250, 400]
}

# Create a DataFrame
df = pl.DataFrame(data)

# Pivot the DataFrame
pivoted_df = df.pivot(index='product_line', columns='month', values='revenue')

# Fill NaN values with 0
pivoted_df = pivoted_df.fill_null(0)

print(pivoted_df)
