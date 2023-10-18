import database.db as db
import socket
import requests
import secrets
import json

def initialize_device(ssid, url):
    db.session.add(db.Raspberry(
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
    db.session.commit()

    raspberry = db.session.query(db.Raspberry).first()

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

def register_device(raspberry: db.Raspberry, url: str):
    configuration = []
    for i in db.SensorsDataModel.model_fields.keys():
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

def initialize_relationship(raspberry, url):
    body = {
        "owner": raspberry.owner,
        "owner_key": raspberry.owner_key,
        "oor-list": []
    }
    payload = json.dumps(body)

    response = requests.post(url + "initialize-relationship", data=payload)
    print("POST '/initialize-relationship':", response.status_code, response.json())

