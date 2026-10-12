import sqlite3
import pandas as pd

def compare_tables(table_name, db_path1, db_path2):
    conn1 = sqlite3.connect(db_path1)
    conn2 = sqlite3.connect(db_path2)

    df1 = pd.read_sql_query(f"SELECT * FROM {table_name};", conn1)
    df2 = pd.read_sql_query(f"SELECT * FROM {table_name};", conn2)

    changes = pd.merge(df1, df2, how='outer', indicator='_merge')

    added = changes[changes['_merge'] == 'left_only']
    removed = changes[changes['_merge'] == 'right_only']
    changed = changes[changes['_merge'] == 'both']

    print("Added Keys:")
    print(added.to_string())
    print("\nRemoved Keys:")
    print(removed.to_string())
    print("\nChanged Keys:")
    print(changed.to_string())

# Use the function
compare_tables("your_table", "path_to_db1.db", "path_to_db2.db")
