install:
#	sudo apt-get install -y mosquitto mosquitto-clients
	sudo apt-get install nmap
	sudo pip3 install -r requirements.txt

run:
    python3 source_code/app.py
    open http://127.0.0.1:5000/
