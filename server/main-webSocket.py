import json
import secrets
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import sessionmaker
import uvicorn
import db
import requests
import socketio
import socket

Session = sessionmaker(bind=db.engine)
session = Session()

app = FastAPI()

sio = socketio.Client()

class SensorsDataModel(BaseModel):
    acceleration: tuple
    pressure: float
    temperature: float
    humidity: float
    battery_percentage: float

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

# Richiesta verso fipy
@sio.event
def read_sensors():
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

    return "OK", 200

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

    # webSocket payload
    if sio.sid is not None:
        webSocket_data = json.dumps(dict(sensorsData))
        sio.emit(event="add_sensors_data", data=webSocket_data)
        print("Message sent!")
    else:
        print("Websocket not connected!")

    return {"message": "Data added successfully"}

@app.on_event("shutdown")
def shutdown_event():
    sio.disconnect()

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
    
    sio.connect('http://192.168.1.8:80/socket.io')
    print('my sid is', sio.sid, sio.get_sid())

    uvicorn.run(app, host="192.168.1.8", port=8000)
