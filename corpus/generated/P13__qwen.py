import pandas as pd
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('example.db')

# Read data from the source table
source_query = "SELECT * FROM source_table"
df = pd.read_sql_query(source_query, conn)

# Perform some transformation on the data
# For example, let's add a new column
df['new_column'] = df['existing_column'] * 2

# Write the transformed data to a different table
target_table = 'target_table'
df.to_sql(target_table, conn, if_exists='replace', index=False)

# Close the connection
conn.close()
