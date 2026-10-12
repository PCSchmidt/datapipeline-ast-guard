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

# Function to convert amounts to USD
def convert_to_usd(transaction):
    rate = exchange_rates[exchange_rates['Currency'] == transaction['Currency']]['Rate'].values[0]
    return transaction['Amount'] * rate

# Apply the conversion function to each row in the transactions dataframe
transactions['Amount_USD'] = transactions.apply(convert_to_usd, axis=1)

print(transactions)
