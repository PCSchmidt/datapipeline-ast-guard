import pandas as pd
from datetime import datetime, timedelta

# Assuming the database connection and cursor are already established
# and the product data is stored in two separate tables: 'products_yesterday' and 'products_today'

# Fetch yesterday's and today's product data
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
today = datetime.now().strftime('%Y-%m-%d')

# Query to get product data from yesterday and today
query_yesterday = f"SELECT * FROM products WHERE date = '{yesterday}'"
query_today = f"SELECT * FROM products WHERE date = '{today}'"

# Execute queries and fetch results into DataFrames
df_yesterday = pd.read_sql(query_yesterday, connection)
df_today = pd.read_sql(query_today, connection)

# Compare the two DataFrames
added_products = df_today[~df_today.isin(df_yesterday)].dropna(how='all')
removed_products = df_yesterday[~df_yesterday.isin(df_today)].dropna(how='all')
changed_products = df_today[df_today.isin(df_yesterday).all(axis=1) == False]

# Print the results
print("Added Products:")
print(added_products)
print("\nRemoved Products:")
print(removed_products)
print("\nChanged Products:")
print(changed_products)
