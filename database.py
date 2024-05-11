from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import configparser

# Read database configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Get database credentials from config
db_credentials = config['postgresql']

# Construct the connection string
connection_string = f"postgresql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database_name']}"

# Create the database engine
engine = create_engine(connection_string)

# Try connecting to the database
# try:
#     engine.connect()
#     print("Connection successful!")
# except Exception as e:
#     print(f"Connection failed: {e}")

# Create declarative base meta instance
Base = declarative_base()

# Create session local class for session maker
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
