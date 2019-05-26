import datetime
import json

import pprint
import imageio
import numpy as np
import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish


MQTT_SERVER = 'localhost'
NUMBER_OF_CAMERAS = 3


def take_photo():
    received = {}

    def on_connect(client, userdata, flags, rc):
        print('Connected with result code ' + str(rc))
        client.subscribe('photo_taken')

    def on_message(client, userdata, msg):
        print(msg.topic + ', ' + str(msg.payload))
        if msg.topic == 'photo_taken':
            photo_data = json.loads(msg.payload)
            received[photo_data['camera_no']] = photo_data

    # Prepare to receive
    client = mqttc.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, 1883, 60)
    #
    # # Send "take photo" signal
    print('Sending "take_photo" signal')
    topic = 'take_photo'
    photo_id = datetime.datetime.now().isoformat()
    publish.single(topic, payload=photo_id, hostname=MQTT_SERVER)

    # Receive photos
    while len(received) < NUMBER_OF_CAMERAS:
        client.loop()
    print('All photos has been received!')
    pprint.pprint(received)

    # Stich
    print('Stiching photo')
    photos_str = [received[cam_no]['photo']
                  for cam_no in range(NUMBER_OF_CAMERAS)]
    photos = [imageio.core.util.Image(np.array(p_str, dtype='uint8'))
              for p_str in photos_str]
    photo_sequence = photos[1:] + photos[::-1][1:]  # [2, 3, 4, 3, 2, 1]
    imageio.mimwrite('gifs/output.gif', photo_sequence, fps=8)
    print('Image successfully saved on disk in /gifs folder')


if __name__ == "__main__":
    take_photo()
