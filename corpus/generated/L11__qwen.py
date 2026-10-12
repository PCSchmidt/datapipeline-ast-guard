import pandas as pd

# Sample data for two snapshots
snapshot1 = pd.DataFrame({
    'id': [1, 2, 3, 4],
    'name': ['Alice', 'Bob', 'Charlie', 'David']
})

snapshot2 = pd.DataFrame({
    'id': [1, 2, 3, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'Eve']
})

# Function to compare two snapshots
def compare_snapshots(snapshot1, snapshot2):
    # Identify keys added in snapshot2
    added = snapshot2[~snapshot2.isin(snapshot1)].dropna()
    
    # Identify keys removed in snapshot2
    removed = snapshot1[~snapshot1.isin(snapshot2)].dropna()
    
    # Identify keys changed in snapshot2
    changed = pd.merge(snapshot1, snapshot2, how='outer', on=['id', 'name'], indicator=True)
    changed = changed[changed['_merge'] == 'both'][snapshot1.columns]
    changed['name_x'] = changed['name_x'].fillna('None')
    changed['name_y'] = changed['name_y'].fillna('None')
    changed['change'] = np.where(changed['name_x'] != changed['name_y'], 'Changed', 'None')
    changed = changed[['id', 'name_x', 'change']]
    changed.columns = ['id', 'name', 'change']
    
    return added, removed, changed

# Compare the snapshots
added, removed, changed = compare_snapshots(snapshot1, snapshot2)

# Print the results
print("Added:")
print(added)
print("\nRemoved:")
print(removed)
print("\nChanged:")
print(changed)
