import pandas as pd

# Sample data: transactions in different currencies
transactions = pd.DataFrame({
    'transaction_id': [1, 2, 3, 4],
    'amount': [100, 200, 150, 300],
    'currency': ['EUR', 'GBP', 'USD', 'JPY']
})

# Sample daily exchange rates
exchange_rates = pd.DataFrame({
    'currency': ['EUR', 'GBP', 'USD', 'JPY'],
    'rate': [1.1, 1.3, 1.0, 0.007]
})

# Convert amounts to USD
def convert_to_usd(amount, currency, exchange_rates):
    rate = exchange_rates.loc[exchange_rates['currency'] == currency, 'rate'].values[0]
    return amount * rate

transactions['amount_usd'] = transactions.apply(
    lambda row: convert_to_usd(row['amount'], row['currency'], exchange_rates), axis=1)

print(transactions)
