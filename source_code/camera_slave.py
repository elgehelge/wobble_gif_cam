import os
import json
import datetime
import random

import numpy
import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish


MQTT_SERVER = 'localhost'
CAMERA_NO = int(os.getenv('CAMERA_NO'))


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
        publish.single('photo_taken', payload, hostname=MQTT_SERVER)
        print('Photo transferred')

    # print('Image successfully saved on disk as ' + gif_file_path)
    # print('Generating GIF')
    # image_paths = [raw_image_path(timestamp, conn.cam_position)
    #                for conn in connections]
    # images = [imageio.imread(path) for path in image_paths]
    # aligned_imgs = img_utils.auto_align(images)
    # # [1, 2, 3, 4] -> [2, 3, 4, 3, 2, 1]
    # images_sequence = aligned_imgs[1:] + aligned_imgs[::-1][1:]
    # gif_id = timestamp
    # gif_file_path = GIF_IMAGE_DIR + gif_id + '.gif'
    # camera_ctrl.ensure_dir_exists(gif_file_path)
    # imageio.mimwrite(gif_file_path, images_sequence, fps=8)


client = mqttc.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_SERVER, 1883, 60)
client.loop_forever()
