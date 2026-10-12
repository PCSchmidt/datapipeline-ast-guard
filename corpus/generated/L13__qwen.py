import polars as pl

# Sample data: orders and refunds
orders = pl.DataFrame({
    "customer_id": [1, 2, 3, 4, 5],
    "order_date": ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05"],
    "amount": [100, 200, 150, 300, 250]
})

refunds = pl.DataFrame({
    "customer_id": [2, 3, 5],
    "refund_date": ["2023-01-03", "2023-01-04", "2023-01-05"],
    "refund_amount": [50, 75, 100]
})

# Calculate customer lifetime value
# 1. Calculate total spending
total_spending = orders.groupby("customer_id").agg(pl.sum("amount")).with_column(pl.col("amount").alias("total_spending"))

# 2. Calculate total refunds
total_refunds = refunds.groupby("customer_id").agg(pl.sum("refund_amount")).with_column(pl.col("refund_amount").alias("total_refunds"))

# 3. Join total spending and total refunds
customer_ltv = total_spending.join(total_refunds, on="customer_id", how="outer").fillna(0)

# 4. Calculate customer lifetime value
customer_ltv = customer_ltv.with_column((pl.col("total_spending") - pl.col("total_refunds")).alias("customer_ltv"))

# 5. Rename columns for clarity
customer_ltv = customer_ltv.rename({"customer_id": "CustomerID", "customer_ltv": "CustomerLifetimeValue"})

print(customer_ltv)
