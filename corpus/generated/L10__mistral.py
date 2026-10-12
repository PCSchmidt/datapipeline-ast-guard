import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# Connect to the SQLite database
conn = sqlite3.connect('database.db')

# Query the users table
users_query = """
SELECT plan_id, COUNT(*) as user_count
FROM users
GROUP BY plan_id
"""

# Query the subscriptions table
subscriptions_query = """
SELECT s.plan_id, MIN(s.start_date) as start_date, MAX(s.end_date) as end_date
FROM subscriptions s
JOIN users u ON s.user_id = u.id
GROUP BY s.plan_id
"""

# Query the invoices table
invoices_query = """
SELECT i.subscription_id, i.amount, i.invoice_date
FROM invoices i
JOIN subscriptions s ON i.subscription_id = s.id
"""

# Execute the queries and store the results as DataFrames
users_df = pd.read_sql_query(users_query, conn)
subscriptions_df = pd.read_sql_query(subscriptions_query, conn)
invoices_df = pd.read_sql_query(invoices_query, conn)

# Merge the subscriptions and invoices DataFrames
invoices_subscriptions_df = pd.merge(subscriptions_df, invoices_df, on='subscription_id')

# Compute monthly recurring revenue per plan
invoices_subscriptions_df['monthly_revenue'] = 0
invoices_subscriptions_df.loc[(invoices_subscriptions_df['invoice_date'] <= invoices_subscriptions_df['end_date']) &
                               (invoices_subscriptions_df['invoice_date'] >= invoices_subscriptions_df['start_date']),
                               'monthly_revenue'] = invoices_subscriptions_df.loc[(invoices_subscriptions_df['invoice_date'] <= invoices_subscriptions_df['end_date']) &
                                                                                  (invoices_subscriptions_df['invoice_date'] >= invoices_subscriptions_df['start_date']),
                                                                                  'amount'].sum() / (invoices_subscriptions_df['end_date'] - invoices_subscriptions_df['start_date']).days

# Merge the users_df and invoices_subscriptions_df
result_df = pd.merge(users_df, invoices_subscriptions_df, on='plan_id')

# Sort the result DataFrame by plan_id and monthly_revenue
result_df = result_df.sort_values(by='plan_id', ignore_index=True)

# Display the result DataFrame
print(result_df)

# Close the connection to the SQLite database
conn.close()
