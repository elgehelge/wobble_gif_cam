import os
import json

import paho.mqtt.client as mqtt


MQTT_SERVER = '192.168.1.84'  # TODO: Make static IP?
CAMERA_NO = os.getenv('CAMERA_NO')


def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe('take_photo')


def on_message(client, userdata, msg):
    print(msg.topic + ', ' + str(msg.payload))
    if msg.topic == 'take_photo':
        photo_id = msg.payload
        # TODO: Snap a photo
        print('Photo taken')
        photo = "" \
            r" PLACEHOLDER " \
            r"  __    __   " \
            r"  \/----\/   " \
            r"   ).  .(    " \
            r"  ( ('') )   " \
            r"   )    (    " \
            r"  /      \   " \
            r" (        )  " \
            r"( \ /--\ / ) " \
            r" w'W    W'w  "
        payload = json.dumps({
            'id': photo_id,
            'photo': photo,
        })
        client.publish('transfer_photo', payload)
        print('Photo transferred')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
