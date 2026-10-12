import polars as pl

# Sample data
data = [
    {"product_line": "A", "month": "2022-01", "revenue": 1000},
    {"product_line": "A", "month": "2022-02", "revenue": 1500},
    {"product_line": "B", "month": "2022-01", "revenue": 2000},
    {"product_line": "B", "month": "2022-02", "revenue": 2500},
]

df = pl.DataFrame(data)

# Parse date and convert to datetime
df = df.with_column(
    pl.col("month").str.split(".").arr.apply(lambda x: pl.date_fromparts(year=int(x[2]), month=int(x[1]), day=1))
)

# Pivot data with monthly revenue by product line
pivot_df = df.pivot(
    "month",
    "product_line",
    "revenue",
    aggregator=pl.sum,
).reset_index()

pivot_df.show()
