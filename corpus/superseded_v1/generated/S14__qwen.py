import pandas as pd

# Define the schema validation function
def validate_schema(df, expected_schema):
    """
    Validate the DataFrame against the expected schema.
    
    Args:
    df (pd.DataFrame): The DataFrame to validate.
    expected_schema (dict): A dictionary where keys are column names and values are the expected data types.
    
    Returns:
    pd.DataFrame: A DataFrame containing only the rows that failed the schema validation.
    """
    # Create a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()
    
    # Iterate over the schema to check each column
    for column, expected_type in expected_schema.items():
        # Check if the column exists in the DataFrame
        if column not in df_copy.columns:
            df_copy[column] = None  # Add a column with None if it doesn't exist
        
        # Filter rows where the data type does not match the expected type
        df_copy['is_valid'] = df_copy[column].apply(lambda x: isinstance(x, expected_type))
        df_copy = df_copy[~df_copy['is_valid']]
    
    # Drop the 'is_valid' column before returning
    df_copy.drop(columns=['is_valid'], inplace=True)
    
    return df_copy

# Define the null rate validation function
def validate_null_rate(df, max_null_rate=0.1):
    """
    Validate the DataFrame against the maximum allowed null rate for each column.
    
    Args:
    df (pd.DataFrame): The DataFrame to validate.
    max_null_rate (float): The maximum allowed null rate for each column.
    
    Returns:
    pd.DataFrame: A DataFrame containing only the rows that failed the null rate validation.
    """
    # Calculate the null rate for each column
    null_rate = df.isnull().mean()
    
    # Identify columns with a null rate higher than the max allowed
    high_null_columns = null_rate[null_rate > max_null_rate].index
    
    # Filter rows where any of the high null columns have a non-null value
    df_copy = df.copy()
    for column in high_null_columns:
        df_copy[column] = df_copy[column].apply(lambda x: x if pd.isnull(x) else None)
    
    return df_copy

# Main function to process the file
def process_file(input_file, output_file, quarantine_file, schema, max_null_rate=0.1):
    """
    Process the input file, validate schema and null rates, and save the results.
    
    Args:
    input_file (str): The path to the input file.
    output_file (str): The path to the output file.
    quarantine_file (str): The path to the quarantine file.
    schema (dict): The expected schema for the DataFrame.
    max_null_rate (float): The maximum allowed null rate for each column.
    """
    # Load the data into a DataFrame
    df = pd.read_csv(input_file)
    
    # Validate schema
    schema_failures = validate_schema(df, schema)
    schema_failures.to_csv(quarantine_file, mode='w', index=False)
    
    # Validate null rate
    null_rate_failures = validate_null_rate(df, max_null_rate)
    null_rate_failures.to_csv(quarantine_file, mode='a', index=False)
    
    # Save the valid data to the output file
    valid_data = df.drop(schema_failures.index).drop(null_rate_failures.index)
    valid_data.to_csv(output_file, mode='w', index=False)

# Example usage
input_file = 'input.csv'
output_file = 'valid_output.csv'
quarantine_file = 'quarantine.csv'
schema = {
    'id': int,
    'name': str,
    'age': int,
    'email': str
}

process_file(input_file, output_file, quarantine_file, schema)
