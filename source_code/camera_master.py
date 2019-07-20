import datetime
import json
import sys

import pprint
import imageio
import numpy as np
import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish

import img_utils


NUMBER_OF_CAMERAS = 4

assert len(sys.argv) == 2, 'Please pass in the IP of the server'
server_ip = sys.argv[1]

# RASPISTILL_SETTINGS = '--rotation 270' \
#                       '--quality 80' \
#                       '--width 640' \
#                       '--height 480' \
#                       '--awb shade' \
#                       '--nopreview'
#


def take_photo():
    print('Capturing started!')
    received = {}

    def on_connect(client, userdata, flags, rc):
        print('Connected with result code ' + str(rc))
        client.subscribe('photo_taken')

    def on_message(client, userdata, msg):
        print(msg.topic + ', ' + str(msg.payload))
        if msg.topic == 'photo_taken':
            photo_data = json.loads(msg.payload.decode("utf-8"))
            received[photo_data['camera_no']] = photo_data

    # Prepare to receive
    client = mqttc.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(server_ip, 1883, 60)
    #
    # # Send "take photo" signal
    print('Sending "take_photo" signal')
    topic = 'take_photo'
    photo_id = datetime.datetime.now().isoformat()
    publish.single(topic, payload=photo_id, hostname=server_ip)

    # Receive photos
    while len(received) < NUMBER_OF_CAMERAS:
        client.loop()
    print('All photos has been received!')
    pprint.pprint(received)

    # Stich
    print('Stiching photo')
    photos_str = [received[cam_no]['photo']
                  for cam_no in range(1, NUMBER_OF_CAMERAS + 1)]
    photos_raw = [imageio.core.util.Image(np.array(p_str, dtype='uint8'))
                  for p_str in photos_str]
    photos = img_utils.auto_align(photos_raw)
    photo_sequence = photos[1:] + photos[::-1][1:]  # [2, 3, 4, 3, 2, 1]
    imageio.mimwrite('gifs/output.gif', photo_sequence, fps=8)
    print('Image successfully saved on disk in /gifs folder')
    image_path = 'gifs/output.gif'
    return image_path


if __name__ == "__main__":
    take_photo()
