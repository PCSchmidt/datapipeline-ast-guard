import pandas as pd

# Sample data
users = pd.DataFrame({
    'user_id': [1, 2, 3, 4, 5],
    'plan': ['Basic', 'Pro', 'Basic', 'Pro', 'Basic']
})

subscriptions = pd.DataFrame({
    'user_id': [1, 2, 3, 4, 5],
    'start_date': ['2023-01-01', '2023-02-15', '2023-01-10', '2023-03-20', '2023-04-01'],
    'end_date': ['2023-02-28', '2023-03-14', '2023-02-29', '2023-04-19', '2023-05-01']
})

invoices = pd.DataFrame({
    'subscription_id': [1, 2, 3, 4, 5],
    'amount': [10, 20, 15, 25, 10]
})

# Joining tables
joined_df = users.merge(subscriptions, on='user_id', how='left')
joined_df = joined_df.merge(invoices, left_on='user_id', right_on='subscription_id', how='left')

# Calculating monthly recurring revenue by plan
joined_df['invoice_month'] = pd.to_datetime(joined_df['end_date']).dt.to_period('M')
mrr_by_plan = joined_df.groupby(['plan', 'invoice_month']).agg({'amount': 'sum'}).unstack(fill_value=0)

print(mrr_by_plan)
