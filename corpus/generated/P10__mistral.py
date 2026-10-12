import pandas as pd

# Load the messy customer table
df = pd.read_csv('customer_table.csv', error_bad_lines=False, skiprows=range(1, 5), skipfooter=1)

# Trim whitespace from column names and data
df.columns = df.columns.str.strip()
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# Standardize phone numbers using a simple replacement rule (replace spaces, hyphens, and parentheses with nothing)
df['phone_number'] = df['phone_number'].str.replace('[ -\(\)]', '')

# Remove duplicates based on email and phone number (assuming they are unique identifiers)
df.drop_duplicates(subset=['email', 'phone_number'], keep='first', inplace=True)

# Save the cleaned customer table
df.to_csv('cleaned_customer_table.csv', index=False)
