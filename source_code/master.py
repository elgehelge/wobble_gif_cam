import datetime

import paho.mqtt.publish as publish


MQTT_SERVER = 'localhost'
NUMBER_OF_CAMERAS = 4


def take_photo():

    # Send order
    print('Sending "take_photo" signal')
    topic = 'take_photo'
    photo_id = datetime.datetime.now().isoformat()
    publish.single(topic, payload=photo_id, hostname=MQTT_SERVER)

    # Collect photos
    # TODO: Spawn a seperate process that waits for all photos and
    # destroys itself
    for cam in range(NUMBER_OF_CAMERAS):
        print('Now collecting photo from camera %s' % cam)

    # Stich
    print('Stiching photo')
    # TODO

# def on_message(client, userdata, msg):
#     print(msg.topic + ', ' + str(msg.payload))
#     if msg.topic == 'transfer_photo':
#         print('Receiving photo with id %s' % id)
#         # TODO: Store photo

#         # TODO: If all photos have been received, then stich!
#         # Cameras are expected to be numbered increasingly from left to
#         # right


take_photo()
