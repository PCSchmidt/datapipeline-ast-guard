import pandas as pd

# Sample data
data = {
    'Category': ['Electronics', 'Electronics', 'Electronics', 'Clothing', 'Clothing', 'Clothing', 'Furniture', 'Furniture', 'Furniture'],
    'Product': ['Laptop', 'Smartphone', 'Tablet', 'T-shirt', 'Jeans', 'Sneakers', 'Chair', 'Desk', 'Coffee Table'],
    'Revenue': [2000, 1500, 1200, 100, 200, 150, 800, 600, 400]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by Category and sort by Revenue in descending order
grouped = df.groupby('Category').apply(lambda x: x.sort_values(by='Revenue', ascending=False).head(10)).reset_index(drop=True)

# Display the result
print(grouped)
