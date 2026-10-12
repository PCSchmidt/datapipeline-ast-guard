import pandas as pd
import numpy as np

# Sample data: DataFrame with store_id, date, and sales_volume
data = {
    'store_id': [1, 1, 1, 2, 2, 2, 3, 3, 3],
    'date': pd.date_range(start='1/1/2023', periods=9, freq='D'),
    'sales_volume': [100, 120, 130, 200, 210, 220, 300, 310, 320]
}

df = pd.DataFrame(data)

# Calculate mean and standard deviation for sales volume per store
store_stats = df.groupby('store_id')['sales_volume'].agg(['mean', 'std']).reset_index()

# Merge store stats back to the original DataFrame
df = pd.merge(df, store_stats, on='store_id', suffixes=('', '_store'))

# Calculate the number of standard deviations away from the mean
df['std_dev_away'] = (df['sales_volume'] - df['sales_volume_store']) / df['std_sales_volume_store']

# Identify anomalous days
anomalous_days = df[(np.abs(df['std_dev_away']) > 3)]['date']

print("Anomalous days with sales volume more than three standard deviations away from the mean:")
print(anomalous_days)
