import pandas as pd

# Sample data
data = {
    'Category': ['Electronics', 'Electronics', 'Electronics', 'Clothing', 'Clothing', 'Clothing', 'Home', 'Home', 'Home'],
    'Product': ['Laptop', 'Smartphone', 'Camera', 'Jeans', 'T-shirt', 'Shoes', 'Furniture', 'Cookware', 'Decor'],
    'Revenue': [1200, 800, 500, 300, 200, 150, 1000, 700, 400]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by Category and sort by Revenue in descending order
df_sorted = df.groupby('Category').apply(lambda x: x.nlargest(10, 'Revenue')).reset_index(drop=True)

# Display the result
print(df_sorted)
