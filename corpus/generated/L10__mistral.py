import polars as pl
import pandas as pd

# Load the data
users = pl.read_csv("users.csv")
subscriptions = pl.read_csv("subscriptions.csv")
invoices = pl.read_csv("invoices.csv")

# Join the tables on user_id and subscription_id
data = users.join(subscriptions, on=["user_id", "subscription_id"], how="left") \
           .join(invoices, on=["user_id", "invoice_id"], how="left")

# Fill missing invoice_amount with 0 and group by subscription_id and plan
data = data.fill_null("invoice_amount", 0).groupby(["subscription_id", "plan"]).agg({"user_id": pl.size(), "invoice_amount": pl.sum()})

# Rename the columns and compute monthly recurring revenue per plan
mrr_df = data.rename({"user_id": "users", "invoice_amount": "total_paid"}) \
             .with_column(pl.col("total_paid") / pl.col("users") * 12) \
             .rename("monthly_recurring_revenue")

# Show the result
mrr_df.show()
