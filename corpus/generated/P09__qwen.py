import pandas as pd

# Sample data for demonstration
data1 = {'id': [1, 2, 3, 4], 'value': ['A', 'B', 'C', 'D']}
data2 = {'id': [2, 3, 4, 5], 'value': ['B', 'C', 'E', 'F']}

# Create DataFrames
df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Find rows added
added = df2[~df2.isin(df1.set_index('id')).any(axis=1)].reset_index(drop=True)
print("Added Rows:")
print(added)

# Find rows removed
removed = df1[~df1.isin(df2.set_index('id')).any(axis=1)].reset_index(drop=True)
print("\nRemoved Rows:")
print(removed)

# Find rows changed
changed = pd.merge(df1, df2, on='id', suffixes=('_old', '_new'))
changed = changed[changed['value_old'] != changed['value_new']]
print("\nChanged Rows:")
print(changed[['id', 'value_old', 'value_new']])
