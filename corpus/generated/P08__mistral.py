import pandas as pd

# Assuming the dataframes 'users', 'subscriptions', and 'invoices' are already loaded

# Merge users and subscriptions on user_id and subscription_id
merged_df = pd.merge(users, subscriptions, on=['user_id', 'subscription_id'])

# Filter rows where invoice_date is greater than or equal to subscription_start_date
# This ensures we only consider active subscriptions for MRR calculation
active_subscriptions = merged_df[merged_df['invoice_date'] >= merged_df['subscription_start_date']]

# Pivot the dataframe to have plan as index and amount as values
# Then, sum the amounts for each plan
mrr_by_plan = active_subscriptions.pivot_table(index='plan', values='amount', aggfunc='sum')

# Rename the index to have plan names
mrr_by_plan.index.name = 'Plan'

# Print the MRR by plan
print(mrr_by_plan)
