# Wobble Gif Cam
Raspberry Pi controlled camera for producing "wobble gifs"

In our setup a Raspberry Pi 3 (master) is used for controlling 3 Raspberry Pi Zeros (connected as USB slaves), each Pi has a camera connected (so 4 cameras in total). The Raspberry pi 3 has a screen attached as well.

# Install
- Clone this repo (`git clone https://github.com/elgehelge/wobble_gif_cam.git`)
- Place yourself in the root of the project `cd wobble_gif_cam`
- run `make install`

# Run the app
- run `python3 source_code/app.py
- open `http://127.0.0.1:5000/` in a browser
