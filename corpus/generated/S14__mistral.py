import pandas as pd
import os
import pyodbc

# Define your incoming file path and SQL Server connection details
incoming_file_path = 'path/to/your/incoming/file.csv'
quarantine_db_server = 'your_quarantine_server'
quarantine_db_name = 'your_quarantine_database'
quarantine_db_user = 'your_quarantine_username'
quarantine_db_password = 'your_quarantine_password'
quarantine_db_driver = '{ODBC Driver 17 for SQL Server}'

# Read the incoming file
data = pd.read_csv(incoming_file_path)

# Define your schema and null rate thresholds
schema = {
    'column1': 'datatype1',
    'column2': 'datatype2',
    # Add more columns as needed
}

null_rate_thresholds = {
    'column1': 0.1,
    'column2': 0.1,
    # Add more columns as needed
}

# Validate schema
expected_schema = data.dtypes.to_dict().keys()
actual_schema = schema.keys()
if expected_schema != actual_schema:
    print(f"Error: Incorrect schema. Expected: {expected_schema}, Actual: {actual_schema}")

# Check null rates
for column, threshold in null_rate_thresholds.items():
    if data[column].isnull().sum() / len(data) > threshold:
        print(f"Error: Null rate for column {column} is {data[column].isnull().sum() / len(data):.2f}, which exceeds the threshold of {threshold}")

# Connect to the quarantine database
conn = pyodbc.connect(
    r'DRIVER=' + quarantine_db_driver + ';SERVER=' + quarantine_db_server + ';DATABASE=' + quarantine_db_name + ';UID=' + quarantine_db_user + ';PWD=' + quarantine_db_password
)

# Create a table to store the quarantined rows
create_table_query = '''
CREATE TABLE IF NOT EXISTS quarantine (
    {0} INT IDENTITY(1,1) PRIMARY KEY,
    {1} VARCHAR(255),
    {2} VARCHAR(255),
    {3} VARCHAR(255),
    {4} VARCHAR(255),
    {5} VARCHAR(255)
)
'''

# Replace column names in the query with the actual column names from the incoming file
columns = list(data.columns)
column_names = ', '.join(columns)
create_table_query = create_table_query.format(column_names, *columns)

# Execute the create table query
conn.cursor().execute(create_table_query)

# Save the quarantined rows
if any(data.isnull().sum(axis=0) > 0):
    quarantine_table = pd.DataFrame(data.loc[data.isnull().any(axis=0)])
    quarantine_table.to_sql('quarantine', conn, if_exists='append', index=False)

# Save the validated data to a new file
validated_data = data.dropna()
validated_data.to_csv('path/to/your/output/validated_file.csv', index=False)
