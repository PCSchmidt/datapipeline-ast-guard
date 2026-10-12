import pandas as pd
from functools import reduce

# Read the CSV file
df = pd.read_csv('sensor_readings.csv')

# Set the date as the index
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)

# Compute the rolling 7-day average for each sensor
def rolling_7day_average(series):
    return series.rolling(window=7, min_periods=1, center=False).mean()

rolling_averages = df.apply(rolling_7day_average)

# Save the results to a new CSV file
rolling_averages.to_frame().T.reset_index().drop(columns=['index']) \
    .rename(columns={df.columns[0]: 'date'}) \
    .to_csv('7day_rolling_average.csv')
