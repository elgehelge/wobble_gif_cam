import datetime
import json

import paho.mqtt.client as mqttc
import paho.mqtt.publish as publish


MQTT_SERVER = 'localhost'
NUMBER_OF_CAMERAS = 2


def take_photo():
    received_photos = {}

    def on_connect(client, userdata, flags, rc):
        print('Connected with result code ' + str(rc))
        client.subscribe('photo_taken')

    def on_message(client, userdata, msg):
        print(msg.topic + ', ' + str(msg.payload))
        if msg.topic == 'photo_taken':
            photo_data = json.loads(msg.payload)
            received_photos[photo_data['camera_no']] = photo_data

    # Prepare to receive
    client = mqttc.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, 1883, 60)

    # Send "take photo" signal
    print('Sending "take_photo" signal')
    topic = 'take_photo'
    photo_id = datetime.datetime.now().isoformat()
    publish.single(topic, payload=photo_id, hostname=MQTT_SERVER)

    # Receive photos
    while len(received_photos) < NUMBER_OF_CAMERAS:
        client.loop()
    print('All photos has been received!')
    print('received', received_photos)

    # Stich
    print('Stiching photo')
    # TODO


if __name__ == "__main__":
    take_photo()
