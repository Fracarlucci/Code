import socketio
import asyncio

sio = socketio.AsyncClient()

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")

async def webSocket_init():
    await sio.connect('http://127.0.0.1:8000')
    print('my sid is', sio.sid)

    # await sio.emit(event='my_event', data={'foo': 'bar'})
    await sio.emit(event="prova", data={"message": "prova"})

    while True:
        await asyncio.sleep(2)
        await sio.emit(event="prova", data={"message": "prova"})

        print("Message sent!")


if __name__ == '__main__':
    asyncio.run(webSocket_init())
    
    