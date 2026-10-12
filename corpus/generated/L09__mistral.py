import polars as pl

def check_schema_and_null_rates(df, output_file):
    # Load the input file
    df_input = pl.read_csv("input.csv")

    # Check the schema of the input dataframe
    print("Input schema:\n", df_input.schema)

    # Check the null rates for each column
    null_rates = df_input.is_null().sum().div(df_input.shape[0])
    print("\nNull rates:\n", null_rates)

    # Filter rows with at least one null value
    df_failing_rows = df_input.filter(df_input.is_null().any(axis=1))

    # Write the failing rows to a new file
    df_failing_rows.write_csv(output_file)
    print(f"\nFailing rows have been written to {output_file}")

check_schema_and_null_rates("input.csv", "failing_rows.csv")
