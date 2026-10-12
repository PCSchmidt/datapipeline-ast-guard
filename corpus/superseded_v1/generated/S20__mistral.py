from google.cloud import storage
import pandas as pd
import pyarrow.parquet as pq

def read_parquet_from_gcs(bucket_name, source_path, destination_df):
    """Read Parquet data from a GCS bucket."""
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.get_blob(source_path)
    table = pq.read_table(blob.download_as_string())
    return destination_df.merge(table, how='outer', indicator=True)

def filter_data(df, column, value):
    """Filter data based on a specific column and value."""
    return df[df[column] == value]

def write_parquet_to_gcs(bucket_name, destination_path, df):
    """Write DataFrame to a Parquet file in a GCS bucket."""
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    table = df.to_arrow().write_table()
    blob = bucket.create_blob(destination_path, data=table.serialize(compression='SNAPPY').to_bytes())

def main():
    source_bucket_name = 'source-bucket-name'
    source_path = 'path/to/source/data.parquet'
    destination_bucket_name = 'destination-bucket-name'
    destination_path = 'path/to/destination/filtered_data.parquet'

    # Load the DataFrame from the source Parquet file
    df = pd.DataFrame()
    try:
        df = read_parquet_from_gcs(source_bucket_name, source_path, df)
    except Exception as e:
        print(f"Error reading data from the source Parquet file: {e}")
        return

    # Filter the DataFrame based on a specific column and value
    filter_column = 'column_name'
    filter_value = 'filter_value'
    df_filtered = filter_data(df, filter_column, filter_value)

    # Write the filtered DataFrame to the destination Parquet file
    try:
        write_parquet_to_gcs(destination_bucket_name, destination_path, df_filtered)
        print(f"Filtered data has been written to {destination_path}.")
    except Exception as e:
        print(f"Error writing data to the destination Parquet file: {e}")

if __name__ == "__main__":
    main()
