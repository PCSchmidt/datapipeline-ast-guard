from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database connection details
DB_USERNAME = "your_username"
DB_PASSWORD = "your_password"
DB_HOST = "your_host"
DB_PORT = "your_port"
DB_NAME = "your_database_name"

# Create engine and session
engine = create_engine(f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
Session = sessionmaker(bind=engine)
session = Session()

# Define the Source and Destination models
Base = declarative_base()
class Source(Base):
    __tablename__ = "source_table"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)

class Destination(Base):
    __tablename__ = "destination_table"
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    age_squared = Column(Integer)

# Query the data from the source table
source_data = session.query(Source).all()

# Transform the data and store in the destination table
for record in source_data:
    destination_record = Destination(
        full_name=f"{record.name} {str(record.age)}",
        age_squared=record.age ** 2
    )
    session.add(destination_record)

# Commit the changes and close the session
session.commit()
session.close()

# Create the destination table if it doesn't exist
Base.metadata.create_all(engine)
