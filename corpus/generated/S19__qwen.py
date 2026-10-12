import pandas as pd

# Sample data for demonstration
users = pd.DataFrame({
    'user_id': [1, 2, 3, 4],
    'plan': ['Basic', 'Pro', 'Pro', 'Basic']
})

subscriptions = pd.DataFrame({
    'subscription_id': [101, 102, 103],
    'user_id': [1, 2, 3],
    'start_date': ['2023-01-01', '2023-02-15', '2023-03-20'],
    'end_date': ['2023-02-28', '2023-03-31', '2023-04-30']
})

invoices = pd.DataFrame({
    'invoice_id': [201, 202, 203],
    'subscription_id': [101, 102, 103],
    'amount': [50, 100, 150],
    'invoice_date': ['2023-02-15', '2023-03-20', '2023-04-25']
})

# Convert date columns to datetime
subscriptions['start_date'] = pd.to_datetime(subscriptions['start_date'])
subscriptions['end_date'] = pd.to_datetime(subscriptions['end_date'])
invoices['invoice_date'] = pd.to_datetime(invoices['invoice_date'])

# Calculate the number of days in each subscription
subscriptions['days_in_subscription'] = (subscriptions['end_date'] - subscriptions['start_date']).dt.days

# Join users and subscriptions
user_subscriptions = pd.merge(users, subscriptions, on='user_id', how='left')

# Join the result with invoices
user_subscriptions_invoices = pd.merge(user_subscriptions, invoices, on='subscription_id', how='left')

# Calculate monthly recurring revenue by plan
monthly_recurring_revenue = user_subscriptions_invoices.groupby(['user_id', 'plan', pd.Grouper(key='invoice_date', freq='M')]).agg(
    total_revenue=('amount', 'sum'),
    total_days=('days_in_subscription', 'sum')
).reset_index()

# Calculate the monthly recurring revenue per plan
monthly_recurring_revenue['mrr'] = monthly_recurring_revenue['total_revenue'] / monthly_recurring_revenue['total_days'] * 30

# Pivot table to get MRR by plan
mrr_by_plan = monthly_recurring_revenue.pivot_table(index='plan', values='mrr', aggfunc='mean')

print(mrr_by_plan)
