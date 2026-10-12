import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, select, update, insert

# Database connection setup
engine = create_engine('your_database_connection_string')
metadata = MetaData()

# Load change data capture data
cdc_data = pd.read_csv('path_to_cdc_data.csv')

# Load existing customer dimension table
customer_dimension = Table('customer_dimension', metadata, autoload_with=engine)

# Create a temporary table to hold the updated data
temp_table_name = 'temp_customer_dimension'
temp_table = Table(temp_table_name, metadata, autoload_with=engine)

# Create the temporary table if it doesn't exist
temp_table.create(bind=engine, checkfirst=True)

# Insert or update the data in the temporary table
with engine.connect() as conn:
    for index, row in cdc_data.iterrows():
        stmt = insert(temp_table).values(row)
        conn.execute(stmt)

# Update the slowly changing dimension table
with engine.connect() as conn:
    # Select all rows from the temporary table
    temp_select = select(temp_table)
    temp_data = conn.execute(temp_select).fetchall()

    # Update the existing customer dimension table
    for row in temp_data:
        # Check if the record exists in the existing table
        existing_select = select(customer_dimension).where(
            customer_dimension.c.customer_id == row['customer_id']
        )
        existing_data = conn.execute(existing_select).fetchone()

        if existing_data:
            # If the record exists, update the end_date and insert the new record
            update_stmt = update(customer_dimension).where(
                customer_dimension.c.customer_id == row['customer_id']
            ).values(
                end_date=row['effective_date'] - pd.Timedelta(days=1),
                updated_by=row['updated_by'],
                updated_date=row['updated_date']
            )
            conn.execute(update_stmt)

            insert_stmt = insert(customer_dimension).values(row)
            conn.execute(insert_stmt)
        else:
            # If the record does not exist, insert it
            insert_stmt = insert(customer_dimension).values(row)
            conn.execute(insert_stmt)

    # Drop the temporary table
    temp_table.drop(bind=engine, checkfirst=True)

print("Slowly Changing Dimension Type 2 update completed.")
