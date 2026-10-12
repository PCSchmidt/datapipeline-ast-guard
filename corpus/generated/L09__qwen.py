import pandas as pd

def check_schema_and_null_rates(input_file, output_file):
    # Read the input file
    df = pd.read_csv(input_file)
    
    # Check schema
    schema = df.dtypes
    
    # Check null rates
    null_rates = df.isnull().mean()
    
    # Identify failing rows (rows with any null values)
    failing_rows = df[df.isnull().any(axis=1)]
    
    # Write failing rows to a separate file
    failing_rows.to_csv(output_file, index=False)
    
    # Print schema and null rates
    print("Schema:\n", schema)
    print("\nNull Rates:\n", null_rates)

# Example usage
input_file = 'input.csv'
output_file = 'failing_rows.csv'
check_schema_and_null_rates(input_file, output_file)
