import communication.svo_comm as svo_comm
from fastapi import FastAPI
import database.db as db
import uvicorn
import socket
import utils

app = FastAPI()

if __name__ == '__main__':
    url = "http://" + socket.gethostbyname(socket.gethostname()) + ":80/"
    raspberry = db.session.query(db.Raspberry).first()
    ssid = utils.get_current_ssid()

    # First time configuration
    if raspberry == None:
        svo_comm.initialize_device(ssid, url)
        raspberry = db.session.query(db.Raspberry).first()
        svo_comm.register_device(raspberry, url)
        svo_comm.initialize_relationship(raspberry, url)    

    utils.set_up_mqtt(raspberry)
    utils.check_location(raspberry, ssid, url)

    uvicorn.run(app, host=raspberry.url, port=8000)
