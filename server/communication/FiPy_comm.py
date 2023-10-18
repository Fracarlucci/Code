import socket

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
