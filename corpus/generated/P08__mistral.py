import pandas as pd

# Load the dataframes
users_df = pd.read_csv('users.csv')
subscriptions_df = pd.read_csv('subscriptions.csv')
invoices_df = pd.read_csv('invoices.csv')

# Merge users, subscriptions, and invoices on user_id
combined_df = pd.merge(users_df, subscriptions_df, on='user_id')
combined_df = pd.merge(combined_df, invoices_df, on='subscription_id')

# Calculate MRR by plan
grouped_df = combined_df.groupby('plan')
mrr_by_plan = grouped_df[['amount']].sum()

# Calculate the number of active subscriptions by plan
active_subscriptions_by_plan = grouped_df['is_active'].sum()

# Calculate MRR per active subscription by plan
mrr_per_active_subscription = mrr_by_plan / active_subscriptions_by_plan

print(mrr_per_active_subscription)
