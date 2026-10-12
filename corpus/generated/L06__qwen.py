import polars as pl

# Sample data: transactions in different currencies and their exchange rates
transactions = pl.DataFrame({
    "transaction_id": [1, 2, 3, 4, 5],
    "amount": [100, 200, 150, 50, 75],
    "currency": ["EUR", "USD", "GBP", "JPY", "CAD"]
})

exchange_rates = pl.DataFrame({
    "currency": ["EUR", "GBP", "JPY", "CAD"],
    "rate_to_usd": [1.15, 1.35, 0.0074, 0.75]
})

# Convert transactions to USD
transactions_with_usd = transactions.join(exchange_rates, on="currency", how="left")
transactions_with_usd = transactions_with_usd.with_column(
    (transactions_with_usd["amount"] * transactions_with_usd["rate_to_usd"]).alias("amount_usd")
).drop(columns=["rate_to_usd", "currency"])

print(transactions_with_usd)
