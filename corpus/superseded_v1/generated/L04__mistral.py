import pandas as pd

# Assuming df is your DataFrame with datetime index and columns 'sensor_1', 'sensor_2', 'sensor_3'
df = pd.DataFrame({
    'sensor_1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'sensor_2': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    'sensor_3': [3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
    'datetime': pd.date_range(start='2022-01-01', periods=10)
})

df['rolling_7day_mean'] = df.groupby(df.datetime.rolling('7D').index)['sensor_1', 'sensor_2', 'sensor_3'].mean().reset_index(level=0, drop=True)

print(df)
