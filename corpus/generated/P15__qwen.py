import pandas as pd

def process_chunk(chunk):
    # Example processing function - calculate mean of a column
    return chunk['your_column_name'].mean()

def load_and_aggregate_csv(file_path, chunk_size=10000):
    results = []
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        result = process_chunk(chunk)
        results.append(result)
    combined_result = sum(results) / len(results)  # Example combining function - average of means
    return combined_result

# Example usage
file_path = 'large_dataset.csv'
result = load_and_aggregate_csv(file_path)
print(f"Combined Result: {result}")
