import pandas as pd

# Sample data
data = {
    'Product': ['A', 'B', 'A', 'C', 'B', 'C'],
    'Month': ['Jan', 'Jan', 'Feb', 'Feb', 'Jan', 'Feb'],
    'Revenue': [100, 200, 150, 250, 120, 220]
}

# Creating DataFrame
df = pd.DataFrame(data)

# Pivot table to transform data
pivot_df = df.pivot(index='Product', columns='Month', values='Revenue')

print(pivot_df)
