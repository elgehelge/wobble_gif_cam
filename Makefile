install:
	sudo apt-get install -y mosquitto mosquitto-clients
	sudo pip3 install -r source_code/requirements.txt
make start_master:
    git pull
	python3 source_code/master.py
make start_slave:
    git pull
	python3 source_code/camera_slave.py
