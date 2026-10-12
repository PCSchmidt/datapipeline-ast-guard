import os
import pandas as pd
from functools import reduce

def read_csv_files(directory):
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.csv')]
    dfs = [pd.read_csv(f) for f in files]
    return dfs

def group_by_region_and_day(df):
    df['date'] = pd.to_datetime(df['date'])
    return df.groupby(['region', 'date']).sum().reset_index()

def save_parquet(dataframe, output_directory, file_name):
    output_path = os.path.join(output_directory, f'{file_name}.parquet')
    dataframe.to_parquet(output_path)
    return output_path

def main(input_directory, output_directory):
    input_files = read_csv_files(input_directory)

    # Combine the dataframes
    combined = reduce(lambda left, right: pd.merge(left, right, on=['region', 'date']), input_files)

    # Group by region and day and sum the revenue
    total_revenue = group_by_region_and_day(combined)

    # Save the total revenue as Parquet files
    output_path = save_parquet(total_revenue, output_directory, 'total_revenue')
    print(f'Saved total revenue as Parquet at {output_path}')

if __name__ == "__main__":
    input_directory = 'input_folder'
    output_directory = 'output_folder'
    main(input_directory, output_directory)
