import pandas as pd

# Sample data
data = {
    'Name': ['  John Doe  ', 'Jane Smith', '  John Doe  '],
    'Phone': [' 123-456-7890 ', ' 9876543210 ', ' 123-456-7890 '],
    'Email': ['john.doe@example.com', 'jane.smith@example.com', 'john.doe@example.com']
}

# Create DataFrame
df = pd.DataFrame(data)

# Trim whitespace
df['Name'] = df['Name'].str.strip()
df['Phone'] = df['Phone'].str.strip()
df['Email'] = df['Email'].str.strip()

# Standardize phone numbers (remove non-digit characters and ensure consistent format)
df['Phone'] = df['Phone'].str.replace(r'\D', '')

# Remove duplicates
df = df.drop_duplicates(keep='first')

# Display the cleaned DataFrame
print(df)
