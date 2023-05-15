import json
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import uvicorn
import db
import requests
import paho.mqtt.publish as publish
import secrets

Session = sessionmaker(bind=db.engine)
session = Session()

app = FastAPI()

class SensorsDataModel(BaseModel):
    acceleration: tuple
    pressure: float
    temperature: float
    humidity: float
    battery_percentage: float

@app.get("/sensors/{id}")
async def read_sensors(id: int):
    query = session.query(db.SensorsData, db.Acceleration)
    if id == 0:
        data = query.join(db.Acceleration).all()
    else:
        data = query.join(db.Acceleration).filter_by(id=id).first()
    if data == None:
        return {"error": "No data found"}
    return data

@app.post("/sensors/")
async def add_sensors_data(sensorsData: SensorsDataModel):
    if len(sensorsData.acceleration) != 3:
        return {"error": "Acceleration must have 3 values (x, y, z)"}
    
    acceleration = db.Acceleration(x=sensorsData.acceleration[0], y=sensorsData.acceleration[1], z=sensorsData.acceleration[2])
    newData = db.SensorsData(dateTime=datetime.now(), acceleration=acceleration, accelerationId=acceleration.id,
                             pressure=sensorsData.pressure, temperature=sensorsData.temperature,
                             humidity=sensorsData.humidity, battery_percentage=sensorsData.battery_percentage)
    session.add(newData)
    session.commit()

    # mqtt publish
    mqttData = json.dumps(dict(sensorsData))
    publish.single(topic="sensors/data", payload=mqttData, hostname="localhost")

    return {"message": "Data added successfully"}
    
if __name__ == '__main__':
    url = " http://10.201.104.210:80/"
    hal_key = secrets.token_bytes(32)
    configuration = []
    for i in SensorsDataModel.__fields__.keys():
        configuration.append({"type": i, "feature": "sensor", "permission": "owner", "schedulable": "true"})

    body = {"brand": "Raspberry-Pi", "model": "3 model B", "hal_key": hal_key.hex(), "configuration": configuration}
    response = requests.post(url + "register", data=body)

    if response.status_code == 200:
        print(response.json())    
    else:
        print("Errore nella chiamata API:", response.status_code)
        
    uvicorn.run(app, host="10.201.104.210", port=8000)
