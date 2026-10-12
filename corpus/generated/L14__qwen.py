import pandas as pd

# Sample data
data = {
    'ProductLine': ['Electronics', 'Clothing', 'Electronics', 'Clothing', 'Electronics'],
    'Month': ['Jan', 'Jan', 'Feb', 'Feb', 'Mar'],
    'Revenue': [1500, 800, 1200, 1000, 1300]
}

# Creating DataFrame
df = pd.DataFrame(data)

# Pivot table to transform data
pivot_df = df.pivot(index='ProductLine', columns='Month', values='Revenue')

# Display the pivot table
print(pivot_df)
