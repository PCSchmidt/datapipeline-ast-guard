import pandas as pd

# Assuming df is your DataFrame and it has columns 'sensor', 'date', and 'reading'
df = pd.DataFrame({
    'sensor': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
    'date': pd.to_datetime(['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05', '2022-01-06', '2022-01-07', '2022-01-08', '2022-01-09']),
    'reading': [1, 2, 3, 4, 5, 6, 7, 8, 9]
})

# Set the date as the index and sort the DataFrame
df.set_index('date', inplace=True)
df.sort_index(inplace=True)

# Compute the 7-day rolling average using the roll() function with a window of 7 days and the mean() aggregation function
df['rolling_7day_avg'] = df.groupby(df.index.roll('7d')).agg(lambda x: x.mean()).reset_index(level=0, drop=True)

print(df)
