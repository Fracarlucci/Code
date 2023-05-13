from fastapi import FastAPI
from network import WLAN
import machine
import urequests as request
import sensors
import json
import time

app = FastAPI()
wlan = WLAN(mode=WLAN.STA)
sleep_time = 60

@app.get("/read-sensors/")
async def read_sensors():
    list = [sensors.get_acceleration(), sensors.get_pressure(), sensors.get_temperature(),
            sensors.get_humidity(), sensors.get_battery_percentage()]
    post = dict()
    for i in list:
        post.update(i)

    jsonPost = json.dumps(post)
    print(jsonPost)

    response = request.post("http://192.168.1.10:8000/sensors/", data=jsonPost) # 10.3.141.1
    print(response.text)

@app.post("/set-schedule/")
async def set_schedule(interval : int):
    global sleep_time
    sleep_time = interval

    return {"message": "Schedule set to " + str(interval) + " seconds"}

print("Trying to connect...   ")
# wlan.connect(ssid='ap_rasp', auth=(WLAN.WPA2, 'password'))
wlan.connect(ssid='Vodafone-A80383340', auth=(WLAN.WPA2, 'HXHfMXLK2dqPMgHL'))

while not wlan.isconnected():
    machine.idle()
    
print("WiFi connected succesfully")
print(wlan.ifconfig())

while True:
    read_sensors()

    time.sleep(sleep_time)
