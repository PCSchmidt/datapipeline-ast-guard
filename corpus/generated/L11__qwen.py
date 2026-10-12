import polars as pl

# Define the two snapshots as DataFrames
snapshot1 = pl.DataFrame({
    "id": [1, 2, 3],
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35]
})

snapshot2 = pl.DataFrame({
    "id": [1, 2, 3, 4],
    "name": ["Alice", "Bob", "Charlie", "David"],
    "age": [25, 30, 35, 40]
})

# Find keys that were added
added_keys = snapshot2.join(snapshot1, on="id", how="right").filter(pl.col("name").is_null()).select("id", "name", "age")

# Find keys that were removed
removed_keys = snapshot1.join(snapshot2, on="id", how="right").filter(pl.col("name").is_null()).select("id", "name", "age")

# Find keys that were changed
changed_keys = snapshot1.join(snapshot2, on="id", how="inner").filter(pl.any(pl.col("name") != pl.col("name_right"), pl.col("age") != pl.col("age_right"))).select("id", "name", "age_right as age")

# Print the results
print("Added keys:")
print(added_keys)
print("\nRemoved keys:")
print(removed_keys)
print("\nChanged keys:")
print(changed_keys)
