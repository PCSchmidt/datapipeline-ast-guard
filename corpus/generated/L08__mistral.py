import polars as pl

def get_top_products_by_category(path_to_data: str):
    df = pl.read_csv(path_to_data)

    # Group by category and sort by revenue in descending order
    grouped = df.groupby("category").sort(pl.desc("revenue"))

    # Select the top 5 products in each group
    top_5_products = grouped.select(pl.frame([
        ("category", "category"),
        ("product_id", "product_id"),
        ("product_name", "product_name"),
        ("revenue", "revenue"),
    ])).top_n(5, "revenue", ascending=False)

    # Remove duplicates by concatenating category and product_id
    unique_top_5_products = top_5_products.alias("result")\
        .with_column(pl.concat_str(["category", "product_id"], separator="_"))\
        .drop_duplicates()

    # Group by the concatenated column and summarize to get the count of each top 5 product in each category
    count_top_5_products = unique_top_5_products.groupby("category").agg([pl.count()])

    # Rename the columns to match the expected output
    count_top_5_products = count_top_5_products.rename({
        "result": "top_5_products_count",
        "count": "count"
    })

    return count_top_5_products

# Run the function with the provided path to the data
result = get_top_products_by_category("sales_data.csv")

# Show the result
result.show()
