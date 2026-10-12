import pandas as pd

# Load the data
df = pd.read_csv('sales_data.csv')

# Group the data by product_category and calculate the total revenue for each product
grouped = df.groupby('product_category').sum('revenue')

# Iterate through each category and find the top 10 products by revenue
top_10_revenue_by_category = {}

for category, revenue_sum in grouped:
    # Sort the products by revenue and select the top 10
    category_products = df[df['product_category'] == category]
    sorted_products = category_products.sort_values('revenue', ascending=False)
    top_10_products = sorted_products.head(10)

    # Store the top 10 products for the category
    top_10_revenue_by_category[category] = top_10_products[['product_id', 'revenue']].reset_index(drop=True)

# Print the results
for category, top_10_products in top_10_revenue_by_category.items():
    print(f"Top 10 Products by Revenue in {category}:")
    print(top_10_products)
