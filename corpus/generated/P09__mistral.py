import pandas as pd
from pandas_gbq import read_big_query
from difflib import get_close_matches

# Set up Google BigQuery credentials
project_id = 'your-project-id'
dataset_id = 'your-dataset-id'
table_id1 = 'your-table-name-1'
table_id2 = 'your-table-name-2'
credentials = json.load(open('path/to/your-service-account-key.json'))

# Read BigQuery tables
df1 = read_big_query(project_id=project_id, dataset_id=dataset_id, table_id=table_id1, credentials=credentials)
df2 = read_big_query(project_id=project_id, dataset_id=dataset_id, table_id=table_id2, credentials=credentials)

# Merge the two dataframes
merged_df = pd.merge(df1, df2, on=None, indicator=True)

# Calculate the difference between the two dataframes
added = merged_df[merged_df['_merge'] == 'left_only']
removed = merged_df[merged_df['_merge'] == 'right_only']
changed = merged_df[merged_df['_merge'] == 'both']

# Compare columns for changes
def compare_columns(column1, column2, threshold=0.85):
    matches = get_close_matches(column1, column2, n=1, cutoff=threshold)

    changed_rows = pd.DataFrame(columns=column1.columns)
    for index, row in column1.iterrows():
        if row not in column2 and len(matches[0][column1.index == index]) > 0:
            changed_rows = changed_rows.append({'index': index, 'old_value': row, 'new_value': matches[0][column1.index[0]]}, ignore_index=True)

    return changed_rows

# Find rows with changes in specific columns
columns_to_compare = ['column1', 'column2', 'column3']
changed_columns = pd.concat([compare_columns(df1[column], df2[column]) for column in columns_to_compare], ignore_index=True)

# Print results
print("Rows added:", added)
print("Rows removed:", removed)
print("Rows changed:", changed)
print("Columns changed:", changed_columns)
