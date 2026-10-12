import polars as pl

def read_csv(file_path):
    return pl.read_csv(file_path)

def merge_transactions_and_exchange_rates(transactions, exchange_rates):
    return transactions.merge(exchange_rates, on="date", how="left")

def convert_transaction_amount_to_usd(df):
    return df.with_column(
        pl.when(
            pl.col("currency") == "USD", pl.col("amount"),
            pl.col("amount") * pl.col("exchange_rate_usd"),
        ).alias("amount_usd")
    )

def main():
    transactions = read_csv("transactions.csv")
    exchange_rates = read_csv("exchange_rates.csv")

    df = merge_transactions_and_exchange_rates(transactions, exchange_rates)
    df = convert_transaction_amount_to_usd(df)

    print(df)

if __name__ == "__main__":
    main()
