import pandas as pd

# Assuming you have DataFrames for users, subscriptions, and invoices
users = pd.DataFrame({
    'user_id': [1, 2, 3, 4],
    'email': ['user1@example.com', 'user2@example.com', 'user3@example.com', 'user4@example.com']
})

subscriptions = pd.DataFrame({
    'subscription_id': [101, 102, 103, 104],
    'user_id': [1, 2, 3, 4],
    'plan': ['Basic', 'Standard', 'Premium', 'Enterprise'],
    'price': [10, 20, 30, 50]
})

invoices = pd.DataFrame({
    'invoice_id': [201, 202, 203, 204],
    'subscription_id': [101, 102, 103, 104],
    'amount': [100, 250, 350, 550],
    'date': pd.to_datetime(['2022-01-01', '2022-02-01', '2022-03-01', '2022-04-01'])
})

# Merge tables on user_id and subscription_id
merged_df = users.merge(subscriptions, on=['user_id', 'subscription_id'], how='left')

# Merge with invoices and filter rows with non-null amounts
merged_df = merged_df.merge(invoices, on='subscription_id', how='left')
merged_df = merged_df[merged_df['amount'].notnull()]

# Calculate monthly recurring revenue by plan
monthly_recurring_revenue = merged_df.groupby('plan')['price'].sum().add(merged_df.groupby('plan')['amount'].sum())

print(monthly_recurring_revenue)
