from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import db

Session = sessionmaker(bind=db.engine)
session = Session()

app = FastAPI()

class SensorsDataModel(BaseModel):
    acceleration: float
    light: float
    pressure: float
    temperature: float
    humidity: float

@app.get("/sensors/{id}")
def read_sensors(id: int):
    query = session.query(db.SensorsData)
    if id == 0:
        data = query.all()
    else:
        data = query.filter_by(id=id).first()
    if data == None:
        return {"error": "No data found"}
    return data

@app.post("/sensors/")
def add_sensors_data(sensorsData: SensorsDataModel):
    newData = db.SensorsData(dateTime = datetime.now() , acceleration=sensorsData.acceleration, light=sensorsData.light,
        pressure=sensorsData.pressure, temperature=sensorsData.temperature, humidity=sensorsData.humidity)
    session.add(newData)
    session.commit()
    return {"message": "Data added successfully"}
    