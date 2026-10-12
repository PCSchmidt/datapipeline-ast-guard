import polars as pl

# Sample data
data = {
    'category': ['Electronics', 'Electronics', 'Electronics', 'Clothing', 'Clothing', 'Clothing', 'Home', 'Home', 'Home'],
    'product': ['Laptop', 'Smartphone', 'Camera', 'Jeans', 'T-shirt', 'Hat', 'Blender', 'Microwave', 'Toaster'],
    'revenue': [1500, 1200, 800, 700, 500, 300, 400, 350, 250]
}

# Create a DataFrame
df = pl.DataFrame(data)

# Group by 'category' and sort within each group by 'revenue' in descending order, then select top 5
top_products = df.groupby('category').select(
    pl.col('category'),
    pl.col('product'),
    pl.col('revenue'),
    pl.col('revenue').nlargest(5).over('category')
).filter(pl.col('revenue').is_in(pl.col('revenue').nlargest(5).over('category')))

# Sort the result by 'category' and 'revenue' in descending order
top_products = top_products.sort(by=['category', 'revenue'], reverse=[False, True])

print(top_products)
