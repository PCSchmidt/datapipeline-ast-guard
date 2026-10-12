import sys
import arrow.parquet as pq
import numpy as np
import pandas as pd

def aggregate_data(data, agg_function):
    grouped = data.groupby(lambda x: None).agg(agg_function)
    return grouped.values[0]

def main():
    input_path = 'data.parquet'
    output_path = 'aggregated_data.parquet'

    # Load the Parquet file lazily
    table = pq.read_table(input_path)

    # Define the aggregation function (sum in this case)
    agg_function = lambda x: np.sum(x)

    # Perform the aggregation
    aggregated_data = aggregate_data(table, agg_function)

    # Create a Pandas DataFrame from the aggregated data
    aggregated_df = pd.DataFrame(aggregated_data, columns=[f"agg_{col.name}" for col in table.schema.fields])

    # Write the aggregated DataFrame to Parquet
    aggregated_df.to_parquet(output_path)

if __name__ == "__main__":
    main()
