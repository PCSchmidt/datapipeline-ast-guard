import pandas as pd

# Sample data: transactions in different currencies
transactions = pd.DataFrame({
    'TransactionID': [1, 2, 3, 4],
    'Amount': [100, 200, 150, 50],
    'Currency': ['EUR', 'USD', 'GBP', 'EUR']
})

# Sample data: daily exchange rates
exchange_rates = pd.DataFrame({
    'Currency': ['EUR', 'USD', 'GBP'],
    'Rate': [0.85, 1.0, 0.75]
})

# Merge transactions with exchange rates
transactions_with_rates = pd.merge(transactions, exchange_rates, on='Currency')

# Calculate the amount in USD
transactions_with_rates['AmountUSD'] = transactions_with_rates['Amount'] * transactions_with_rates['Rate']

# Drop the unnecessary currency column
transactions_with_rates = transactions_with_rates.drop(columns=['Currency', 'Rate'])

print(transactions_with_rates)
