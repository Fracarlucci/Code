from sqlalchemy import create_engine, Column, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///sensors.db')

Base = declarative_base()

class SensorsData(Base):
    __tablename__ = 'sensorsData'
    id = Column(Integer, primary_key=True)
    dateTime = Column(DateTime)
    acceleration = Column(Float)
    light = Column(Float)
    pressure = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)

Base.metadata.create_all(engine)
