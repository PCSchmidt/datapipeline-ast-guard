import pandas as pd

# Load transaction data (assuming transaction_data.csv has columns 'date', 'amount')
transaction_data = pd.read_csv('transaction_data.csv')

# Load exchange rate data (assuming exchange_rates.csv has columns 'date', 'exchange_rate')
exchange_rates = pd.read_csv('exchange_rates.csv')

# Merge transaction and exchange rate data based on the date column
combined_data = transaction_data.merge(exchange_rates, on='date')

# Multiply transaction amounts by exchange rates to convert to USD
combined_data['usd_amount'] = combined_data['amount'] * combined_data['exchange_rate']

# Save the result to a new CSV file (assuming output_file.csv)
combined_data[['date', 'usd_amount']].to_csv('output_file.csv', index=False)
