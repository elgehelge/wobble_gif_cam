import os
import json
import datetime

import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish


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
        # Remove the 3 lines below when we have a real camera working
        photo = np.zeros([10, 10])  # placeholder 10x10 image
        photo[:,random.random.randint(0,9)] = 1  # add random line
        print('Photo taken')
        payload = json.dumps({
            'camera_no': CAMERA_NO,
            'id': photo_id,
            'photo': photo.tostring(),
            'timestamp': datetime.datetime.now().isoformat(),
        })
        publish.single('photo_taken', payload, hostname=MQTT_SERVER)
        print('Photo transferred')


client = mqttc.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
client.loop_forever()
