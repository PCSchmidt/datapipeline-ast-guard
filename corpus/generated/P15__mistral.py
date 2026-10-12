import pandas as pd

def chunksize(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def load_and_aggregate_csv(file_path, chunk_size=100000):
    df_list = []

    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Aggregate each chunk (Replace 'column_1' and 'agg_func' with your specific column and aggregation function)
        chunk['agg_result'] = chunk['column_1'].agg('sum')
        df_list.append(chunk)

    # Combine the results
    result_df = pd.concat(df_list)

    return result_df

# Replace 'file_path' with the path to your CSV file
result_df = load_and_aggregate_csv('your_file.csv')
