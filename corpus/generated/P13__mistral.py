import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('example.db')

# Read data from the source table
df = pd.read_sql_query("SELECT * FROM source_table", conn)

# Perform data transformation (for example, adding a new column)
df['new_column'] = df['column_1'] * df['column_2']

# Write the transformed data to the target table
df.to_sql('target_table', conn, if_exists='replace', index=False)

# Close the database connection
conn.close()
