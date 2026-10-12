import sqlalchemy
from sqlalchemy import create_engine, event, orm
from sqlalchemy.orm import sessionmaker
import pandas as pd
import pyodbc

# Source Database connection
source_connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                                   'SERVER=your_server;'
                                   'DATABASE=your_database;'
                                   'UID=your_username;'
                                   'PWD=your_password')

# Destination Database connection
destination_connection = sqlalchemy.create_engine('sqlite:///customer_dimension.db')

# Create tables in the destination database
metadata = sqlalchemy.MetaData()
customer_dim = sqlalchemy.Table('customer_dim', metadata,
    sqlalchemy.Column('customer_id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('customer_name', sqlalchemy.String),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
    sqlalchemy.Column('is_active', sqlalchemy.Boolean)
)
metadata.create_all(destination_connection)

# Source and destination session binds
source_session = sessionmaker(bind=source_connection)()
destination_session = sessionmaker(bind=destination_connection)()

# Create a function to be triggered on update events
@event.listens_for(source_session.query(source_customer_dim), 'before_update')
def on_source_customer_dim_update(mapper, connection, target):
    # Get the original state of the row
    original_state = source_session.query(source_customer_dim).filter_by(id=target.id).first()

    # Create a new row in the destination table with the original state
    if original_state:
        original_state_dict = original_state.__dict__
        original_state_dict['updated_at'] = original_state.created_at
        destination_session.merge(original_state, create_only=True)
        original_state_dict['id'] = None
        destination_session.merge(original_state_dict)

# CDC script
source_query = source_session.query(source_customer_dim).with_only_columns(['customer_id', 'customer_name', 'is_active']).subquery()

with source_connection.connection() as source_con:
    with destination_connection.connection() as dest_con:
        source_con.cursor().execute(f'TRUNCATE TABLE {source_customer_dim.__tablename__}')
        source_con.cursor().execute(f"SELECT * FROM {source_query}")
        source_data = pd.DataFrame(source_con.cursor().fetchall(), columns=[i[0] for i in source_con.cursor().description])
        source_data['created_at'] = pd.to_datetime(source_data['created_at'].apply(lambda x: x[0]))
        source_data['updated_at'] = pd.to_datetime(source_data['updated_at'].apply(lambda x: x[0]))

        source_data.loc[source_data['customer_id'].duplicated(), 'is_active'] = False

        source_data.to_sql('source_customer_dim', dest_con, if_exists='append', index=False)
