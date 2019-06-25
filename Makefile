install:
	sudo apt-get install -y mosquitto mosquitto-clients
	sudo pip3 install -r source_code/requirements.txt
make start_master:
	python3 source_code/master.py 192.168.50.1
make start_camera:
	python3 source_code/camera_slave.py 192.168.50.1
