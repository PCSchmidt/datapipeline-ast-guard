import pandas as pd

# Assuming the tables are already loaded into DataFrames
users = pd.DataFrame({
    'user_id': [1, 2, 3, 4],
    'plan': ['Basic', 'Premium', 'Basic', 'Premium']
})

subscriptions = pd.DataFrame({
    'subscription_id': [101, 102, 103, 104],
    'user_id': [1, 2, 3, 4],
    'start_date': ['2021-01-01', '2021-02-15', '2021-01-20', '2021-03-10'],
    'end_date': ['2021-02-28', '2021-03-14', '2021-02-19', '2021-04-09']
})

invoices = pd.DataFrame({
    'invoice_id': [201, 202, 203, 204],
    'subscription_id': [101, 102, 103, 104],
    'amount': [10, 20, 10, 20],
    'invoice_date': ['2021-01-15', '2021-02-20', '2021-02-25', '2021-03-15']
})

# Convert date columns to datetime
subscriptions['start_date'] = pd.to_datetime(subscriptions['start_date'])
subscriptions['end_date'] = pd.to_datetime(subscriptions['end_date'])
invoices['invoice_date'] = pd.to_datetime(invoices['invoice_date'])

# Join tables
joined_df = pd.merge(users, subscriptions, on='user_id')
joined_df = pd.merge(joined_df, invoices, on='subscription_id')

# Calculate monthly recurring revenue per plan
monthly_revenue = joined_df.groupby([joined_df['invoice_date'].dt.to_period('M'), 'plan']).agg({'amount': 'sum'}).reset_index()
monthly_revenue.rename(columns={'amount': 'monthly_revenue'}, inplace=True)

print(monthly_revenue)
