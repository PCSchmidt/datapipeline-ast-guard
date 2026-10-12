import pandas as pd

# Load the exchange rate table
exchange_rates = pd.read_csv('exchange_rates.csv')
exchange_rates.set_index('Date', inplace=True)

# Load the transaction amounts
transactions = pd.read_csv('transactions.csv')

# Merge transactions with exchange rates based on the date
converted_transactions = transactions.merge(exchange_rates, left_on='Date', right_index=True)

# Multiply transaction amounts by the exchange rate to convert to USD
converted_transactions['Amount_USD'] = converted_transactions['Amount'] * converted_transactions['USD']

# Save the converted transactions
converted_transactions.to_csv('converted_transactions.csv', index=False)
