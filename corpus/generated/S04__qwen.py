import pandas as pd

# Sample data for visits, add-to-cart, purchase, and marketing campaigns
data = {
    'campaign': ['Campaign A', 'Campaign A', 'Campaign A', 'Campaign B', 'Campaign B', 'Campaign B', 'Campaign C', 'Campaign C', 'Campaign C'],
    'activity': ['visit', 'add-to-cart', 'purchase', 'visit', 'add-to-cart', 'purchase', 'visit', 'add-to-cart', 'purchase'],
    'user_id': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    'timestamp': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05', '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09']
}

# Create DataFrame
df = pd.DataFrame(data)

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Sort by campaign and timestamp
df = df.sort_values(by=['campaign', 'timestamp'])

# Calculate conversion rates
conversion_rates = df.groupby('campaign').apply(lambda x: (x['activity'] == 'purchase').mean()).reset_index(name='conversion_rate')

# Print conversion rates
print("Funnel Report with Conversion Rates:")
print(conversion_rates)
