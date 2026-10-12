import pandas as pd
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('example.db')

# Read data from the source table
df = pd.read_sql_query("SELECT * FROM source_table", conn)

# Perform data transformation
# Example transformation: convert 'age' column to string and add ' years' suffix
df['age'] = df['age'].astype(str) + ' years'

# Write the transformed data to a new table
df.to_sql('transformed_table', conn, if_exists='replace', index=False)

# Close the database connection
conn.close()
