import pandas as pd

# Load the dataset (assuming you have a CSV file with the following columns: 'user_id', 'campaign_id', 'visit', 'add_to_cart', 'purchase')
data = pd.read_csv('marketing_data.csv')

# Prepare the data for the funnel report
funnel_data = data.groupby(['campaign_id', 'user_id']).agg({
    'visit': 'count',
    'add_to_cart': 'first',
    'purchase': 'last'
}).reset_index(drop=False)

# Filling NA values for 'add_to_cart' and 'purchase' with 0
funnel_data.fillna(0, inplace=True)

# Calculate conversion rates
funnel_data[['visit_to_add_to_cart', 'add_to_cart_to_purchase']] = funnel_data[['add_to_cart', 'purchase']].div(funnel_data['visit'], axis=0)

# Group the data by campaign_id and calculate the total visitors, add-to-cart, purchases, and conversion rates
campaign_funnel = funnel_data.groupby('campaign_id').agg({
    'visit': 'sum',
    'add_to_cart': 'sum',
    'purchase': 'sum',
    'visit_to_add_to_cart': 'mean',
    'add_to_cart_to_purchase': 'mean'
}).reset_index()

print(campaign_funnel)
