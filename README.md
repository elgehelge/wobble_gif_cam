# Wobble Gif Cam
Raspberry Pi controlled camera for producing "wobble gifs"

In our setup a Rasberry Pi 3 is used for controling 3 Rasberry Pi Zeros, each Pi has a camera connected (4 cameras in total).

# Install
1. Setup a WiFi access point on the Raspberry Pi 3, by following this guid: https://learn.sparkfun.com/tutorials/setting-up-a-raspberry-pi-3-as-an-access-point/all
- Clone this repo (`git clone https://github.com/elgehelge/wobble_gif_cam.git`)
- Place yourself in the root of the project `cd wobble_gif_cam`
- run `make install`

# Run the app
- run `python3 source_code/app.py
- open `http://127.0.0.1:5000/` in a browser
