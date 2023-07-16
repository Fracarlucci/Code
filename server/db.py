from sqlalchemy import create_engine, Column, ForeignKey, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

engine = create_engine('sqlite:///./server/sensors.db', connect_args={"check_same_thread": False})

Base = declarative_base()

class SensorsData(Base):
    __tablename__ = 'sensorsData'
    id = Column(Integer, primary_key=True)
    dateTime = Column(DateTime)
    pressure = Column(Float)
    temperature = Column(Float)
    humidity = Column(Float)
    battery_percentage = Column(Float)

    accelerationId = Column(Integer, ForeignKey('acceleration.id'))
    acceleration = relationship("Acceleration", backref=backref("sensorsData", uselist=False))

class Acceleration(Base):
    __tablename__ = 'acceleration'
    id = Column(Integer, primary_key=True)

    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    
Base.metadata.create_all(engine)
