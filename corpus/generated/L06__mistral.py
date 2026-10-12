import csv
from datetime import datetime
from collections import defaultdict

# Read exchange rate data
exchange_rates = defaultdict(float)
with open('exchange_rates.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    for row in reader:
        exchange_rates[datetime.strptime(row[0], '%Y-%m-%d')] = float(row[1])

# Read transactions data
transactions = []
with open('transactions.csv', newline='') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header
    for row in reader:
        transaction_date = datetime.strptime(row[0], '%Y-%m-%d')
        transaction_amount = float(row[1])
        transactions.append((transaction_date, transaction_amount))

# Convert transaction amounts to USD
converted_transactions = []
for transaction in transactions:
    date = transaction[0]
    amount = transaction[1]
    rate = exchange_rates[date]
    usd_amount = amount * rate
    converted_transactions.append((date, usd_amount))

# Write converted transaction data to a new CSV file
with open('converted_transactions.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['date', 'usd_amount'])
    for transaction in converted_transactions:
        writer.writerow(transaction)
