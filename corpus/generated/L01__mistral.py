import os
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

def read_csv_files(directory):
    csv_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.csv')]
    dfs = [pd.read_csv(file) for file in csv_files]
    return dfs

def merge_and_compute_revenue(dfs):
    merged_df = pd.concat(dfs, ignore_index=True)
    merged_df['revenue'] = merged_df['revenue'].astype(float)
    merged_df.groupby(['region', 'date'])['revenue'].sum().reset_index().rename(columns={'revenue': 'revenue_per_day'})
    return merged_df

def save_as_parquet(df, output_directory):
    table = pa.Table.from_pandas(df)
    schema = table.schema
    output_file = os.path.join(output_directory, f'revenue_per_region_per_day.parquet')
    pq.write_table(table, output_file)

def main():
    input_directory = 'path/to/csv/files'
    output_directory = 'path/to/output/parquet/files'

    csv_files = read_csv_files(input_directory)
    merged_df = merge_and_compute_revenue(csv_files)
    save_as_parquet(merged_df, output_directory)

if __name__ == '__main__':
    main()
