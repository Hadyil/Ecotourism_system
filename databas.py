import sqlite3
import pandas as pd
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# SQLAlchemy setup
Base = declarative_base()
engine = create_engine("sqlite:///./eco_sys.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Database connection
conn = sqlite3.connect('eco_sys.db')

# Load data from CSV files
activities_df = pd.read_csv('activities.csv')
destinations_df = pd.read_csv('destinations.csv')


# Insert data into tables
activities_df.to_sql('activities', conn, if_exists='replace', index=False)
destinations_df.to_sql('destinations', conn, if_exists='replace', index=False)


# Commit changes and close connection
conn.commit()
conn.close()



