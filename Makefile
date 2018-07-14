install:
	sudo apt-get install -y mosquitto mosquitto-clients
	sudo pip install paho-mqtt

run-camera:
	git pull
	python source_code/camera.py

run-camera:
	git pull
	python source_code/camera.py
