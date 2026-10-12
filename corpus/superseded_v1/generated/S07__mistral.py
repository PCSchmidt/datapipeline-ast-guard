import pandas as pd

# Read the CSV files
transactions = pd.read_csv('transactions.csv')
exchange_rates = pd.read_csv('exchange_rates.csv')

# Ensure both dataframes have the same format for date column
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])
exchange_rates['date'] = pd.to_datetime(exchange_rates['date'])

# Merge the dataframes based on the date
merged = pd.merge(transactions, exchange_rates, on='date')

# Multiply the transaction amount by the exchange rate to convert to USD
merged['amount_usd'] = merged['amount'] * merged['usd_rate']

# Save the result to a new CSV file
merged[['id', 'amount_usd']].to_csv('converted_transactions.csv', index=False)
