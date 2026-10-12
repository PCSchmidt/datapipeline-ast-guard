import pandas as pd

# Sample data
data = {
    'Category': ['Electronics', 'Electronics', 'Electronics', 'Clothing', 'Clothing', 'Clothing', 'Furniture', 'Furniture', 'Furniture', 'Home Appliances'],
    'Product': ['Laptop', 'Smartphone', 'Camera', 'T-shirt', 'Jeans', 'Dress', 'Chair', 'Desk', 'Sofa', 'Blender'],
    'Revenue': [1200, 900, 800, 50, 30, 100, 600, 400, 200, 80]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by Category and sort within each group by Revenue in descending order
df_sorted = df.sort_values(by=['Category', 'Revenue'], ascending=[True, False])

# Get the top 10 products in each category
top_10_products = df_sorted.groupby('Category').head(10)

print(top_10_products)
