from network import WLAN
import machine
import urequests
import sensors
import json
import time
import usocket
import ussl
import _thread

wlan = WLAN(mode=WLAN.STA)
sleep_time = 10

# Connect to WiFi
if not wlan.isconnected():
    print("Trying to connect...   ")
    # wlan.connect(ssid='ap_rasp', auth=(WLAN.WPA2, 'password'))
    wlan.connect(ssid='Vodafone-A80383340', auth=(WLAN.WPA2, 'HXHfMXLK2dqPMgHL'))

    while not wlan.isconnected():
        machine.idle()
        
    print("WiFi connected succesfully")
    print(wlan.ifconfig())

# Function to read sensors and send data to server
def read_sensors(seconds: int = 0):
    list = [sensors.get_acceleration(), sensors.get_pressure(), sensors.get_temperature(),
            sensors.get_humidity(), sensors.get_battery_percentage()]
    post = dict()

    for i in list:
        post.update(i)

    jsonPost = json.dumps(post)
    print(jsonPost)

    response = urequests.post("http://192.168.1.8:8000/sensors/", data=jsonPost) # 10.3.141.1

    print(response.text)

    if seconds != 0:
        print("Sleeping for", seconds, "seconds...")
        time.sleep(seconds)

    return response.text

# Function to handle client requests
def handle_client(client_socket):
    print("Client connected!")

    request = client_socket.readline().decode().strip()

    if request.startswith("GET"):
        path = request.split()[1]
        print("Received GET request for:", path)

        if path == "/read-sensors":
            
            response = read_sensors(0)

            if "error" not in response:
                response = "HTTP/1.1 200 OK\r\n\r\n" + response
            
            else:
                response = "HTTP/1.1 500 Internal Server Error\r\n\r\n" + response.text
        
        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n 404 Error: Page not found"

    elif request.startswith("POST"):

        path = request.split()[1]
        print("Received POST request for:", path)

        if path == "/set-schedule":

            interval = request.split()[2]

            print("Received interval:", interval)

            global sleep_time
            sleep_time = interval

            response = {"message": "Schedule set to " + str(interval) + " seconds"}

            print(response)

            response = "HTTP/1.1 200 OK\r\n\r\n" + response.text

        else:
            response = "HTTP/1.1 404 Not Found\r\n\r\n 404 Error: Page not found"

    client_socket.write(response.encode())
    client_socket.close()

# Create a socket
server_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
server_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)

server_address = ('192.168.1.11', 8000)
server_socket.bind(server_address)

server_socket.listen(5)

print("Ready to accept connections...")

# threading.Timer(5, read_sensors).start()

while True:
 
    client_socket, client_address = server_socket.accept()

    _thread.start_new_thread(handle_client, (client_socket, ))

    # _thread.start_new_thread(read_sensors, (10, ))

# print("Sleeping...")
# time.sleep(60)
# response = read_sensors()

