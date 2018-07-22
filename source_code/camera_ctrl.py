"""
Thanks to nallic for providing a big portion of this code at
https://github.com/nallic/pi3dscanner/
"""

import shutil
import os
import socket
from typing import Iterator

import nmap
import spur


HOSTS = '172.20.10.0/24'  # for iOS 6 and 7
DEFAULT_USERNAME = 'pi'
DEFAULT_PASSWORD = 'raspberry'
TEMP_IMAGE_PATH = '/tmp/wobble_gif_cam_latest_capture.jpg'
RASPISTILL_SETTINGS = '--rotation 270 --quality 80 --width 640 --height 480 --awb shade'


def discover_pis(include_this_device=False) -> Iterator[str]:
    if include_this_device:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            this_ip = s.getsockname()[0]
            yield this_ip
    nm = nmap.PortScanner()
    scan = nm.scan(hosts=HOSTS, arguments='-sn', sudo=True)
    for unit_ip, unit_values in scan['scan'].items():
        vendors = list(unit_values['vendor'].values())
        if len(vendors) > 0 and vendors[0] == 'Raspberry Pi Foundation':
            yield unit_ip


def connect_device(ip: str) -> spur.ssh.SshShell:
    print('connecting to ' + ip)
    shell = spur.SshShell(hostname=ip, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD,
                          missing_host_key=spur.ssh.MissingHostKey.accept)
    cam_position = shell.run(['cat', 'WOBBLE_GIF_CAM_POSITION']).output.decode().strip()
    shell.cam_position = cam_position
    shell.ip = ip
    print('connected to ' + ip + ' with camera position ' + cam_position)
    return shell


def setup_for_capture(connection) -> spur.ssh.SshProcess:
    # cleanup all devices
    connection.run(['killall', '-w', '-s', 'USR2', 'raspistill'], allow_error=True)  # kill old sessions
    # start raspistill
    print('Connecting to cam at position ' + connection.cam_position)
    raspistill_process = connection.spawn(['raspistill', '-o', TEMP_IMAGE_PATH, '-t', '0', *RASPISTILL_SETTINGS.split(), '-s'], store_pid=True)
    return raspistill_process


def copy_remote_file(connection: spur.ssh.SshShell, remote_file_path: str, local_file_path: str) -> None:
    print('Copying remote ' + TEMP_IMAGE_PATH + ' from cam no. ' + connection.cam_position + ' to local ' + local_file_path)
    ensure_dir_exists(local_file_path)
    with connection.open(remote_file_path, "rb") as remote_file:
        with open(local_file_path, "wb") as local_file:
            shutil.copyfileobj(remote_file, local_file)


def ensure_dir_exists(path: str):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
