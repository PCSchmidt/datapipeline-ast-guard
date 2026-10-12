import pandas as pd

# Assuming df is the input dataframe
def find_top_10_in_each_category(df):
    grouped = df.groupby('category').agg({'revenue': ('top_10', lambda x: x.nlargest(10))})
    grouped.columns = [col[2] for col in grouped.columns]
    return grouped

# Assume the dataframe has columns: 'id', 'product_name', 'category', 'revenue'
df = pd.DataFrame({
    'id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    'product_name': ['Product A', 'Product B', 'Product C', 'Product D', 'Product E', 'Product F', 'Product G', 'Product H', 'Product I', 'Product J', 'Product K', 'Product L', 'Product M', 'Product N', 'Product O'],
    'category': ['Category A', 'Category A', 'Category A', 'Category B', 'Category B', 'Category B', 'Category C', 'Category C', 'Category C', 'Category A', 'Category A', 'Category A', 'Category B', 'Category B', 'Category B'],
    'revenue': [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 1000, 2000, 3000, 4000, 5000, 6000]
})

result = find_top_10_in_each_category(df)
print(result)
