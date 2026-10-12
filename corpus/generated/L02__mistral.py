import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('your_database.db')

# Query the orders table for orders within the last 90 days
last_90_days_orders = pd.read_sql_query("SELECT customer_id FROM orders WHERE strftime('%Y-%m-%d', order_date) >= strftime('%Y-%m-%d', 'now' - 90)", conn)

# Query the customers table and join with the last_90_days_orders dataframe to find customers with no orders in the last 90 days
customers_with_no_orders = pd.read_sql_query("SELECT customers.customer_name, customers.customer_id FROM customers LEFT JOIN last_90_days_orders ON customers.customer_id = last_90_days_orders.customer_id WHERE customers.customer_id IS NULL", conn)

# Print the customers with no orders in the last 90 days
print(customers_with_no_orders)

# Close the connection
conn.close()
