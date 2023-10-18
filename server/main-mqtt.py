import json
import pywifi
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
    server_address = ('10.3.141.177', 8000) # 192.168.1.11
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
    raspberry = session.query(db.Raspberry).first()
    mqttData = json.dumps(dict(sensorsData))
    publish.single(topic=raspberry.hal_key+"/post-sensors", payload=mqttData, hostname="broker.mqtt-dashboard.com")

    return {"message": "Post request successfull"}

def initialize_device():
    session.add(db.Raspberry(
        id=1,
        hal_key=secrets.token_bytes(32).hex(),
        unregister_key=secrets.token_bytes(32).hex(),
        owner_key="key",#secrets.token_bytes(32).hex(),
        url=socket.gethostbyname(socket.gethostname()),
        brand="Raspberry-Pi",
        model="3 model B",
        owner="Francesco",
        location=ssid
    ))
    session.commit()

    raspberry = session.query(db.Raspberry).first()

    body = {
        "owner": raspberry.owner,
        "owner_key": raspberry.owner_key,
        "unregister_key": raspberry.unregister_key,
        "url": raspberry.url
    }
    
    payload = json.dumps(body)
    response = requests.post(url + "initialize", data=payload)

    if response.status_code == 200:
        print(response.json())   
    else:
        print("Errore nella chiamata API:", response.status_code, response.text)
        db.Raspberry.__table__.drop(db.engine)
        db.engine.dispose()
        exit(1)

def register_device(raspberry: db.Raspberry, ssid: str):
    configuration = []

    for i in SensorsDataModel.model_fields.keys():
        configuration.append({
            "event": "sensor",
            "type": i,
            "feature": "",
            "permission": "private",
            "schedulable": "True"
        })

    body = {
        "brand": "Raspberry-Pi",
        "model": "3 model B",
        "hal_key": raspberry.hal_key,
        "configuration": configuration,
        "location": raspberry.location
    }
    
    payload = json.dumps(body)
    response = requests.post(url + "register", data=payload)
    print("POST '/register':", response.status_code, response.json())

def initialize_relationship():
    body = {
        "owner": raspberry.owner,
        "owner_key": raspberry.owner_key,
        "oor-list": []
    }
    payload = json.dumps(body)

    response = requests.post(url + "initialize-relationship", data=payload)
    print("POST '/initialize-relationship':", response.status_code, response.json())

def get_current_ssid():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]

    iface.scan()
    scan_results = iface.scan_results()

    for result in scan_results:
        if result.ssid:
            current_ssid = result.ssid
            break

    return current_ssid

def check_location():
    print("Checking location...")
    if(ssid != raspberry.location):
        raspberry.location = ssid
        raspberry.url = socket.gethostbyname(socket.gethostname())
        session.commit()

        body = {"location": raspberry.location, "url": raspberry.url}
        payload = json.dumps(body)

        response = requests.post(url + "update-vo-info", data=payload)
        print("POST '/update-vo-info':", response.status_code, response.json())
     
if __name__ == '__main__':
    url = "http://" + socket.gethostbyname(socket.gethostname()) + ":80/"
    raspberry = session.query(db.Raspberry).first()
    ssid = get_current_ssid()

    # First time configuration
    if raspberry == None:
        initialize_device()
        raspberry = session.query(db.Raspberry).first()
        register_device(raspberry, ssid)
        initialize_relationship()    

    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    client.connect("broker.mqtt-dashboard.com", 1883, 60)
    client.subscribe(raspberry.hal_key + "/read-sensors", 0)
    client.loop_start()

    check_location()

    uvicorn.run(app, host=raspberry.url, port=8000)
