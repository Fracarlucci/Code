import json
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import uvicorn
import db
import requests
import paho.mqtt.client as paho
import paho.mqtt.publish as publish
import secrets
import socket

Session = sessionmaker(bind=db.engine)
session = Session()

app = FastAPI()

class SensorsDataModel(BaseModel):
    acceleration: tuple
    pressure: float
    temperature: float
    humidity: float
    battery_percentage: float

# Richiesta verso fipy
def on_message(mosq, obj, msg):
    print("Richiesta verso fipy")
    server_address = ('192.168.1.11', 8000)
    path = "/read-sensors"

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(server_address)
    print("Connected to the server:", server_address)

    request = "GET {} HTTP/1.1\r\nHost: {}\r\n\r\n".format(path, server_address[0])
    client_socket.send(request.encode())

    response = client_socket.recv(1024).decode()

    client_socket.close()

def on_publish(mosq, obj, mid):
    pass

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
    result = publish.single(topic="sensors/post_data", payload=mqttData, hostname="broker.mqtt-dashboard.com")

    return {"message": "Data added successfully"}
    
if __name__ == '__main__':
    # TODO aggiustare registrazione
    # url = " http://10.201.104.210:80/"
    # hal_key = secrets.token_bytes(32)
    # configuration = []
    # for i in SensorsDataModel.__fields__.keys():
    #     configuration.append({"type": i, "feature": "sensor", "permission": "owner", "schedulable": "true"})

    # body = {"brand": "Raspberry-Pi", "model": "3 model B", "hal_key": hal_key.hex(), "configuration": configuration}
    # response = requests.post(url + "register", data=body)

    # if response.status_code == 200:
    #     print(response.json())    
    # else:
    #     print("Errore nella chiamata API:", response.status_code)

    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    #client.tls_set('ca.crt', certfile='server.crt', keyfile='server.key')
    client.connect("broker.mqtt-dashboard.com", 1883, 60)
    client.subscribe("sensors/get_data", 0)
    client.loop_start()

    uvicorn.run(app, host="192.168.1.8", port=8000)
