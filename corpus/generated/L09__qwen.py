import polars as pl

def check_schema_and_null_rates(input_file, output_file):
    # Read the input file
    df = pl.read_csv(input_file)
    
    # Check schema
    print("Schema of the DataFrame:")
    print(df.schema)
    
    # Check null rates
    null_counts = df.is_null().sum()
    total_counts = df.shape[0]
    null_rates = null_counts / total_counts
    print("\nNull rates of each column:")
    print(null_rates)
    
    # Identify failing rows (rows with any null values)
    failing_rows = df.filter(pl.any(pl.col(pl.all()).is_null()))
    
    # Write failing rows to a separate file
    failing_rows.write_csv(output_file)
    print(f"\nFailing rows have been written to {output_file}")

# Example usage
input_file = 'input.csv'
output_file = 'failing_rows.csv'
check_schema_and_null_rates(input_file, output_file)
