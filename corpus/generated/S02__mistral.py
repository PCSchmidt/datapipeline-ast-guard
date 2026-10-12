from sqlalchemy import create_engine, MetaData, Table, select, func
from sqlalchemy.sql.functions import current_timestamp
from datetime import timedelta

# Define the connection string
conn_str = "sqlite:///your_database.db"

# Create an engine
engine = create_engine(conn_str)

# Reflect the metadata from the database
metadata = MetaData()
orders = Table('orders', metadata, autoload_with=engine)
customers = Table('customers', metadata, autolack_with=engine)

# Find customers who have not placed an order in the last 90 days
no_orders_in_90_days = metadata.bind.execute(
    select([customers]).
    where(
        customers.c.id.notin_(
            select([orders.c.customer_id]).
            where(orders.c.order_date > (current_timestamp() - timedelta(days=90)))
        )
    )
)

# Print the results
for row in no_orders_in_90_days:
    print(row)
