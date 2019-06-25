import os
import sys
import json
import datetime
import random

import numpy
import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish


assert len(sys.argv) == 2, 'Please pass in the IP of the server'
server_ip = sys.argv[1]
parent_dir = os.path.join(os.path.dirname(__file__), '..')
with open(os.path.join(parent_dir, 'WOBBLE_GIF_CAM_POSITION'), 'r') as fp:
    CAMERA_NO = int(fp.readline())


def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('take_photo')


def on_message(client, userdata, msg):
    print(msg.topic + ', ' + str(msg.payload))
    if msg.topic == 'take_photo':
        photo_id = msg.payload
        # TODO: Snap a photo
        # Remove the 3 lines below when we have a real camera working
        photo = numpy.zeros([10, 10])  # placeholder 10x10 image
        photo[:, random.randint(0, 9)] = 255  # add random line
        print('Photo taken')
        payload = json.dumps({
            'camera_no': CAMERA_NO,
            'id': photo_id,
            'photo': photo.tolist(),
            'timestamp': datetime.datetime.now().isoformat(),
        })
        publish.single('photo_taken', payload, hostname=server_ip)
        print('Photo transferred')


client = mqttc.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(server_ip, 1883, 60)
client.loop_forever()
