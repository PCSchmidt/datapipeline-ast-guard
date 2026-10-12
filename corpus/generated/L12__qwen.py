import pandas as pd

# Define the path to the Parquet file
parquet_file_path = 'path_to_your_parquet_file.parquet'

# Lazily load the Parquet file using pandas
# This allows for on-the-fly data processing without loading everything into memory
df = pd.read_parquet(parquet_file_path, engine='auto', engine_kwargs={'use_threads': True})

# Aggregate the data (example: summing a column named 'value')
aggregated_result = df.groupby('category')['value'].sum().reset_index()

# Define the path to save the aggregated result
output_file_path = 'path_to_save_aggregated_result.parquet'

# Write the aggregated result to a new Parquet file
aggregated_result.to_parquet(output_file_path, engine='auto', engine_kwargs={'compression': 'snappy'})

print(f"Aggregated result has been saved to {output_file_path}")
