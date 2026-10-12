import pandas as pd

# Define the path to your large CSV file
csv_path = 'path_to_your_large_csv.csv'

# Define the chunk size
chunk_size = 10000

# Initialize an empty DataFrame to store the aggregated results
aggregated_results = pd.DataFrame()

# Use pandas' read_csv function with chunksize parameter
for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
    # Aggregate the chunk (example: summing a column named 'value')
    chunk_aggregated = chunk.groupby('category').agg({'value': 'sum'}).reset_index()
    
    # Append the aggregated chunk to the overall results
    aggregated_results = pd.concat([aggregated_results, chunk_aggregated], ignore_index=True)

# Optionally, reset the index of the final aggregated results
aggregated_results = aggregated_results.reset_index(drop=True)

# Display the final aggregated results
print(aggregated_results)
