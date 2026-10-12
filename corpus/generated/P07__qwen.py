import pandas as pd

# Sample data creation
data = {
    'StoreID': [1, 1, 1, 2, 2, 2],
    'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-01', '2023-01-02', '2023-01-03']),
    'Sales': [100, 150, 120, 200, 250, 220]
}

# Create DataFrame
df = pd.DataFrame(data)

# Group by StoreID and calculate mean and standard deviation of sales
df['StoreMeanSales'] = df.groupby('StoreID')['Sales'].transform('mean')
df['StoreSalesStd'] = df.groupby('StoreID')['Sales'].transform('std')

# Define thresholds for unusual sales (3 standard deviations from the mean)
df['IsUnusual'] = (df['Sales'] < df['StoreMeanSales'] - 3 * df['StoreSalesStd']) | \
                   (df['Sales'] > df['StoreMeanSales'] + 3 * df['StoreSalesStd'])

# Filter for unusual sales
unusual_sales = df[df['IsUnusual']]

print(unusual_sales)
