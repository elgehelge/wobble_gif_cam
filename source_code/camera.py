import os

import paho.mqtt.client as mqtt


MQTT_SERVER = 'localhost'  # TODO: Make static IP?
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
        payload = {
            'id': photo_id,
            'photo': photo,
        }
        client.publish.single('transfer_photo', payload, hostname=MQTT_SERVER)
        print('Photo transferred')


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, 1883, 60)

client.loop_forever()
