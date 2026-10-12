import pandas as pd

# Function to compare two DataFrames
def compare_tables(df1, df2):
    # Find rows added in df2
    added = df2[~df2.isin(df1)].dropna()
    
    # Find rows removed in df2
    removed = df1[~df1.isin(df2)].dropna()
    
    # Find rows that have changed
    changed = pd.concat([df1, df2]).drop_duplicates(keep=False)
    
    return added, removed, changed

# Example usage
df1 = pd.DataFrame({'id': [1, 2, 3], 'value': [10, 20, 30]})
df2 = pd.DataFrame({'id': [1, 2, 3, 4], 'value': [10, 20, 30, 40]})

added, removed, changed = compare_tables(df1, df2)

print("Added Rows:")
print(added)

print("\nRemoved Rows:")
print(removed)

print("\nChanged Rows:")
print(changed)
