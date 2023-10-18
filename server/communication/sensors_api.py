from main_mqtt import app, session, db
import paho.mqtt.publish as publish
from datetime import datetime
import database.db as db
import json

@app.get("/sensors/{id}")
async def read_sensors(id: int):
    query = session.query(db.SensorsData, db.Acceleration)
    if id == 0:
        data = query.join(db.Acceleration).all()
    elif id == -1:
        data = query.join(db.Acceleration).order_by(db.SensorsData.dateTime.desc()).first()
    else:
        data = query.join(db.Acceleration).filter_by(id=id).first()
    if data == None:
        return {"error": "No data found"}
    return data

@app.post("/sensors/")
async def add_sensors_data(sensorsData: db.SensorsDataModel):
    if len(sensorsData.acceleration) != 3:
        return {"error": "Acceleration must have 3 values (x, y, z)"}
    
    acceleration = db.Acceleration(x=sensorsData.acceleration[0], y=sensorsData.acceleration[1], z=sensorsData.acceleration[2])
    newData = db.SensorsData(dateTime=datetime.now(), acceleration=acceleration, accelerationId=acceleration.id,
                             pressure=sensorsData.pressure, temperature=sensorsData.temperature,
                             humidity=sensorsData.humidity, battery_percentage=sensorsData.battery_percentage)
    session.add(newData)
    session.commit()

    # mqtt publish
    raspberry = session.query(db.Raspberry).first()
    mqttData = json.dumps(dict(sensorsData))
    publish.single(topic=raspberry.hal_key+"/post-sensors", payload=mqttData, hostname="broker.mqtt-dashboard.com")

    return {"message": "Post request successfull"}