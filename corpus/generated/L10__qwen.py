import polars as pl

# Sample data for users
users = pl.DataFrame({
    "user_id": [1, 2, 3, 4],
    "email": ["alice@example.com", "bob@example.com", "charlie@example.com", "dave@example.com"],
    "plan": ["Basic", "Premium", "Basic", "Premium"]
})

# Sample data for subscriptions
subscriptions = pl.DataFrame({
    "subscription_id": [1, 2, 3, 4],
    "user_id": [1, 2, 3, 4],
    "start_date": ["2023-01-01", "2023-02-01", "2023-03-01", "2023-01-01"],
    "end_date": ["2023-02-28", "2023-03-31", "2023-04-30", "2023-02-28"],
    "plan": ["Basic", "Premium", "Basic", "Premium"]
})

# Sample data for invoices
invoices = pl.DataFrame({
    "invoice_id": [1, 2, 3, 4],
    "subscription_id": [1, 2, 3, 4],
    "amount": [10, 20, 10, 20],
    "invoice_date": ["2023-01-15", "2023-02-28", "2023-03-15", "2023-02-14"]
})

# Convert dates to Date type for easier manipulation
users = users.with_column(pl.col("start_date").cast(pl.Date))
users = users.with_column(pl.col("end_date").cast(pl.Date))
subscriptions = subscriptions.with_column(pl.col("start_date").cast(pl.Date))
subscriptions = subscriptions.with_column(pl.col("end_date").cast(pl.Date))
invoices = invoices.with_column(pl.col("invoice_date").cast(pl.Date))

# Join tables
joined_df = users.join(subscriptions, on="user_id")
joined_df = joined_df.join(invoices, on="subscription_id")

# Compute monthly recurring revenue per plan
def calculate_mrr(df):
    df = df.with_column(pl.col("invoice_date").dt.month().alias("invoice_month"))
    df = df.group_by(["plan", "invoice_month"]).agg(pl.sum("amount").alias("mrr"))
    return df

mrr_df = calculate_mrr(joined_df)

print(mrr_df)
