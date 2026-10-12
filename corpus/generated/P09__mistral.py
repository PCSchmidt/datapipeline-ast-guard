import pandas as pd

def compare_dataframes(df1, df2, on=None, threshold=None):
    if on is None:
        merged = pd.merge(df1, df2, how='outer')
    else:
        merged = pd.merge(df1, df2, on=on, how='outer')

    # Check rows added
    added = merged[~df1.index.isin(df2.index) & (merged.shape[0] > 1)]

    # Check rows removed
    removed = merged[df1.index.isin(df2.index) & (merged.shape[0] == 0)]

    # Check rows changed (merged rows where at least one column is different)
    changed = merged[~df1.eq(df2, na_action='ignore').all(axis=1)]

    # Threshold to ignore small differences (e.g., small difference in floats or timestamps)
    if threshold is not None:
        changed = changed[abs(changed - df2).abs(df1).gt(threshold)]

    return {'added': added, 'removed': removed, 'changed': changed}

# Example usage:
df1 = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
df2 = pd.DataFrame({'A': [1, 2, 3, 10], 'B': [4, 5, 6, 11], 'C': [7, 8, 9, 12]})

result = compare_dataframes(df1, df2, on=['A', 'B'])
print(result)
