import pandas as pd

# Assuming the data is already loaded in a DataFrame named df

# Group the data by category and sort by revenue in descending order
grouped = df.groupby('category').sort_values(by='revenue', ascending=False)

# Iterate through each category and find the top 10 products by revenue
results = {}
for name, data in grouped:
    top_10 = data.head(10)
    results[name] = top_10['product_id'].values

# Print the results
for category, products in results.items():
    print(f"Top 10 products by revenue in {category}:")
    print(products)
