import pandas as pd
from google.cloud import storage
from datetime import datetime, timedelta

# Set up GCS client
storage_client = storage.Client()

# Define source and destination buckets
source_bucket_name = 'your-source-bucket'
destination_bucket_name = 'your-destination-bucket'

# Get the current date and calculate the date of last month
now = datetime.now()
last_month = now - timedelta(days=30)

# List all Parquet files in the source bucket
bucket = storage_client.get_bucket(source_bucket_name)
blobs = bucket.list_blobs(prefix='last_month_data/', delimiter='/', match_glob='*.parquet')

# Filter and read the data
filtered_data = pd.DataFrame()
for blob in blobs:
    # Parse the date from the blob name
    date_str = blob.name.split('_')[1].split('.')[0]
    blob_date = datetime.strptime(date_str, '%Y%m')
    
    # Skip if the date is not from last month
    if blob_date != last_month:
        continue
    
    # Read the Parquet file into a DataFrame
    df = pd.read_parquet(blob.public_url)
    filtered_data = pd.concat([filtered_data, df])

# Filter the data based on some condition (example: age > 30)
filtered_data = filtered_data[filtered_data['age'] > 30]

# Write the filtered data to the destination bucket
destination_bucket = storage_client.get_bucket(destination_bucket_name)
with pd.ExcelWriter(filtered_data.to_excel('filtered_data.xlsx', index=False)) as writer:
    filtered_data.to_excel(writer, sheet_name='Sheet1', index=False)

# Upload the Excel file to the destination bucket
destination_blob = destination_bucket.blob('filtered_data.xlsx')
destination_blob.upload_from_filename('filtered_data.xlsx')

print('Data processed and saved to destination bucket.')
