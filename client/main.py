from network import WLAN
import machine
import urequests as request
import sensors
import json
import time

wlan = WLAN(mode=WLAN.STA)

print("Trying to connect...")
wlan.connect(ssid='Vodafone-A80383340', auth=(WLAN.WPA2, 'HXHfMXLK2dqPMgHL'))

while not wlan.isconnected():
    machine.idle()
    
print("WiFi connected succesfully")
print(wlan.ifconfig())

while True:
    list = [sensors.get_acceleration(), sensors.get_pressure(), sensors.get_temperature(),
        sensors.get_humidity(), sensors.get_battery_percentage()]
    post = dict()
    for i in list:
        post.update(i)

    jsonPost = json.dumps(post)
    print(jsonPost)

    response = request.post("http://192.168.1.10:8000/sensors/", data=jsonPost)
    print(response.text)

    time.sleep(60)