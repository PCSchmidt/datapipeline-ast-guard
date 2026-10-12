import pandas as pd

# Assuming df is your DataFrame
df = pd.DataFrame({
    'product_id': ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8', 'P9', 'P10'],
    'product_name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E', 'Product F', 'Product G', 'Product H', 'Product I', 'Product J'],
    'category': ['Category A', 'Category A', 'Category A', 'Category B', 'Category B', 'Category B', 'Category C', 'Category C', 'Category C', 'Category C'],
    'revenue': [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]
})

# Group data by category and sort by revenue in descending order
grouped = df.groupby('category').sort_values(by='revenue', ascending=False)

# Iterate through each group and print the top 5 products by revenue
for name, group in grouped:
    print(f"Top 5 products in {name}:")
    print(group.head(5))
    print("\n")
