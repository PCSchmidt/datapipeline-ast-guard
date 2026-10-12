import pandas as pd

# Assuming df is your DataFrame with timestamps as index
df = pd.read_csv('sensors_data.csv', index_col='timestamp')

# Set the date-time column as the index
df = df.set_index('timestamp')

# Calculate the rolling 7-day average for each sensor
rolling_7day_avg = df.rolling(window=7, min_periods=1, center=False).mean()

# Save the rolling average back to a new CSV file
rolling_7day_avg.to_csv('rolling_7day_avg.csv')
