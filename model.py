from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Database engine and session setup
engine = create_engine("sqlite:///./eco_sys.db") 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Destination(Base):
    __tablename__ = 'destinations'
    __table_args__ = {'extend_existing': True} 
    Site_ID = Column(Integer, primary_key=True,  autoincrement=True)
    Circuit_Type = Column(String, nullable=True)
    Region = Column(String, nullable=False)
    Site_Name = Column(String, index=True,)
    Description = Column(String, nullable=False)
    Best_Time_to_Visit = Column(String, nullable=False)


class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = {'extend_existing': True} 
    Activity_ID = Column(Integer, primary_key=True, index=True)
    Activity_Name = Column(String, nullable=False)
    Description = Column(String, nullable=False)
    Duration = Column(String, nullable=False)


from database import Base


class ActivitiesModel(Base):  # Inherit from Base (SQLAlchemy declarative base)
    __tablename__ = "activities"  # Database table name
    __table_args__ = {'extend_existing': True} 
    Activity_ID = Column(Integer, primary_key=True, index=True)
    Activity_Name = Column(String)
    Description = Column(String)
    Duration = Column(String)

class DestinationsModel(Base):  # Inherit from Base (SQLAlchemy declarative base)
    __tablename__ = "destinations"  # Database table name
    __table_args__ = {'extend_existing': True} 
    Site_ID = Column(Integer, primary_key=True, index=True, nullable=True)  # Primary key for the destinations
    Circuit_Type = Column(String)  # Type of circuit (e.g., Earth Memory Circuit)
    Region = Column(String)  # Region where the destination is located
    Site_Name = Column(String)  # Name of the site
    Description = Column(String)  # Description of the site
    Best_Time_to_Visit = Column(String)  




   