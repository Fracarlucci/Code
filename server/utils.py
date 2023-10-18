import communication.FiPy_comm as FiPy_comm
import paho.mqtt.client as paho
import database.db as db
import requests
import pywifi
import socket
import json

def set_up_mqtt(raspberry):
    client = paho.Client()
    client.on_message = FiPy_comm.on_message
    client.on_publish = FiPy_comm.on_publish
    client.connect("broker.mqtt-dashboard.com", 1883, 60)
    client.subscribe(raspberry.hal_key + "/read-sensors", 0)
    client.loop_start()

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

def check_location(raspberry, ssid, url):
    print("Checking location...")
    if(ssid != raspberry.location):
        raspberry.location = ssid
        raspberry.url = socket.gethostbyname(socket.gethostname())
        db.session.commit()

        body = {"location": raspberry.location, "url": raspberry.url}
        payload = json.dumps(body)

        response = requests.post(url + "update-vo-info", data=payload)
        print("POST '/update-vo-info':", response.status_code, response.json())
     