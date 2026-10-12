import pandas as pd
import re

def trim_whitespace(df):
    for col in df.columns:
        df[col] = df[col].str.strip()
    return df

def standardize_phone_numbers(df):
    phone_regex = re.compile(r'(\+\d{1,3}\s?)?\(?\d{3}\)?\s?[-.]\s?\d{3}\s?[-.]\s?\d{4}')
    df['Phone Number'] = df['Phone Number'].apply(lambda x: phone_regex.sub('', x).strip())
    return df

def remove_duplicates(df):
    unique_rows = df.drop_duplicates()
    return unique_rows

customer_df = pd.read_csv('messy_customer_data.csv')  # replace 'messy_customer_data.csv' with your file path

customer_df = trim_whitespace(customer_df)
customer_df = standardize_phone_numbers(customer_df)
customer_df = remove_duplicates(customer_df)

customer_df.to_csv('cleaned_customer_data.csv', index=False)
