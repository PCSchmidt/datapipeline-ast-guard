import pandas as pd

# Sample data
data = {
    'Name': ['  John Doe  ', 'Jane Smith', '  John Doe  '],
    'Phone': [' 123-456-7890 ', '  9876543210 ', '123-456-7890'],
    'Email': ['johndoe@example.com', 'janesmith@example.com', 'johndoe@example.com']
}

# Create DataFrame
df = pd.DataFrame(data)

# Trim whitespace
df['Name'] = df['Name'].str.strip()
df['Phone'] = df['Phone'].str.strip()
df['Email'] = df['Email'].str.strip()

# Standardize phone numbers to a consistent format
df['Phone'] = df['Phone'].str.replace('[- ]', '', regex=True)

# Remove duplicates
df = df.drop_duplicates()

# Reset index
df.reset_index(drop=True, inplace=True)

print(df)
