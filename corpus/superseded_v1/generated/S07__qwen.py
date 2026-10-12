import pandas as pd

# Assuming you have two DataFrames: 'transactions' and 'exchange_rates'
# 'transactions' has a 'transaction_date' and 'amount_in_local_currency'
# 'exchange_rates' has 'date' and 'exchange_rate_to_usd'

# Convert 'transaction_date' to datetime in both DataFrames
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
exchange_rates['date'] = pd.to_datetime(exchange_rates['date'])

# Merge 'transactions' with 'exchange_rates' on the date to get the exchange rate for each transaction
merged_df = pd.merge(transactions, exchange_rates, left_on='transaction_date', right_on='date', how='left')

# Convert the 'amount_in_local_currency' to USD using the 'exchange_rate_to_usd'
merged_df['amount_in_usd'] = merged_df['amount_in_local_currency'] * merged_df['exchange_rate_to_usd']

# Drop the 'date' column from the merged DataFrame as it's no longer needed
merged_df.drop(columns=['date'], inplace=True)

# Optionally, you can round the 'amount_in_usd' to a certain number of decimal places
merged_df['amount_in_usd'] = merged_df['amount_in_usd'].round(2)

# Display the resulting DataFrame
print(merged_df)
