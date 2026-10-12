import pandas as pd

# Sample data creation
data = {
    'category': ['Electronics', 'Electronics', 'Electronics', 'Clothing', 'Clothing', 'Clothing', 'Home', 'Home', 'Home'],
    'product': ['Laptop', 'Smartphone', 'Camera', 'Jeans', 'T-shirt', 'Hat', 'Blender', 'Microwave', 'Toaster'],
    'revenue': [1500, 1200, 800, 700, 500, 300, 400, 350, 250]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by category and sort within each group by revenue in descending order
df_sorted = df.sort_values(by=['category', 'revenue'], ascending=[True, False])

# Get the top 5 products in each category
top_products = df_sorted.groupby('category').head(5)

# Reset index for better readability
top_products.reset_index(drop=True, inplace=True)

# Display the result
print(top_products)
