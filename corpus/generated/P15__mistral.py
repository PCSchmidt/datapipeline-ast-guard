import pandas as pd

def load_and_aggregate(file_path, chunksize=100000, aggfunc='sum'):
    df_list = []

    with pd.read_csv(file_path, chunksize=chunksize) as df_reader:
        for chunk in df_reader:
            df_list.append(chunk.groupby(None).aggregate({'value': aggfunc}))

    return pd.concat(df_list)

# Usage
result = load_and_aggregate('large_file.csv')
print(result)
