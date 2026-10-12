import pandas as pd

def check_schema_and_null_rates(input_file, output_file):
    try:
        df = pd.read_csv(input_file)
        schema = df.dtypes
        null_rates = df.isnull().sum() / len(df)

        print("Schema:")
        print(schema)
        print("\nNull Rates:")
        print(null_rates)

        failing_rows = df[df.isnull().any(axis=1)]
        failing_rows.to_csv(output_file, index=False)
        print(f"\nFailing Rows Saved to: {output_file}")

    except Exception as e:
        print(f"Error reading the input file: {e}")

# Example usage:
check_schema_and_null_rates('input.csv', 'failing_rows.csv')
