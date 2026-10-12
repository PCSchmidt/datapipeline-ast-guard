import pandas as pd

# Sample data
users = pd.DataFrame({
    'user_id': [1, 2, 3, 4, 5],
    'plan': ['Basic', 'Pro', 'Basic', 'Pro', 'Basic']
})

subscriptions = pd.DataFrame({
    'user_id': [1, 2, 3, 4, 5],
    'start_date': ['2023-01-01', '2023-02-15', '2023-03-20', '2023-04-25', '2023-05-30'],
    'end_date': ['2023-02-28', '2023-03-14', '2023-04-19', '2023-05-24', '2023-06-29']
})

invoices = pd.DataFrame({
    'invoice_id': [101, 102, 103, 104, 105],
    'user_id': [1, 2, 3, 4, 5],
    'amount': [10, 20, 10, 20, 10],
    'invoice_date': ['2023-01-15', '2023-03-20', '2023-04-25', '2023-06-01', '2023-07-05']
})

# Convert date columns to datetime
users['start_date'] = pd.to_datetime(users['start_date'])
users['end_date'] = pd.to_datetime(users['end_date'])
invoices['invoice_date'] = pd.to_datetime(invoices['invoice_date'])

# Function to calculate monthly recurring revenue
def calculate_mrr(subscriptions, invoices, months=12):
    # Create a date range for the specified number of months
    date_range = pd.date_range(start=subscriptions['start_date'].min(), periods=months, freq='M')
    
    # Initialize MRR DataFrame
    mrr = pd.DataFrame(date_range, columns=['invoice_date'])
    mrr['mrr'] = 0
    
    # Loop through each month and calculate MRR
    for date in date_range:
        # Filter subscriptions that overlap with the month
        overlapping_subs = subscriptions[(subscriptions['start_date'] <= date) & (subscriptions['end_date'] >= date)]
        
        # Filter invoices for the overlapping subscriptions
        overlapping_invoices = invoices[invoices['user_id'].isin(overlapping_subs['user_id']) & (invoices['invoice_date'] <= date)]
        
        # Calculate MRR for the month
        mrr.loc[mrr['invoice_date'] == date, 'mrr'] = overlapping_invoices['amount'].sum()
    
    # Merge with users to get plan information
    mrr = mrr.merge(users[['user_id', 'plan']], on='user_id', how='left')
    
    return mrr

# Calculate MRR
mrr_df = calculate_mrr(subscriptions, invoices)

# Display the MRR DataFrame
print(mrr_df)
