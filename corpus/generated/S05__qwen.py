import pandas as pd

# Assuming df is your DataFrame and it has columns 'sensor' and 'reading'
df['rolling_7_day_avg'] = df.groupby('sensor')['reading'].rolling(window=7).mean().reset_index(level=0, drop=True)
