import pandas as pd

# Load the tables
orders = pd.read_csv('orders.csv')
refunds = pd.read_csv('refunds.csv')

# Merge the orders and refunds tables on customer_id
merged = pd.merge(orders, refunds, on='customer_id')

# Fill missing order_date and refund_date with NaT
merged.fillna({'order_date': pd.NaT, 'refund_date': pd.NaT}, inplace=True)

# Sort the data by order_date and group by customer_id
grouped = merged.sort_values(['customer_id', 'order_date']) \
               .groupby('customer_id')

# Initialize an empty list to store customer CLVs
clvs = []

# Iterate through each group (customer) and calculate the CLV
for name, group in grouped:
    customer_clv = sum(group['order_value'].loc[group['order_date'].notnull()] \
                       ) - sum(group['order_value'].loc[group['refund_date'].notnull()])
    clvs.append(customer_clv)

# Save the calculated CLVs in a DataFrame
clv_df = pd.DataFrame(clvs, columns=['CLV'])
clv_df['customer_id'] = clvs.index

# Save the CLV DataFrame to a CSV file
clv_df.to_csv('customer_clv.csv', index=False)
