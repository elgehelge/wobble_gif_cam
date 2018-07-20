"""
Thanks to nallic for providing a big portion of this code at
https://github.com/nallic/pi3dscanner/
"""

import time
import shutil
import datetime
import os
import socket
from typing import Iterator

import nmap
import spur
import imageio


HOSTS = '172.20.10.0/24'  # for iOS 6 and 7
DEFAULT_USERNAME = 'pi'
DEFAULT_PASSWORD = 'raspberry'
TEMP_IMAGE_PATH = '/tmp/wobble_gif_cam_latest_capture.jpg'
RAW_IMAGE_DIR = 'wobble_gif_cam/captured_raw/'
GIF_IMAGE_DIR = 'wobble_gif_cam/captured_gif/'
RASPISTILL_SETTINGS = '--rotation 90 --quality 30 --width 640 --height 480'


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
    print('connected to ' + ip + ' with camera position ' + cam_position)
    return shell


def end_sessions(sessions: [spur.ssh.SshProcess]) -> None:
    for session in sessions:
        session.send_signal('SIGUSR2')
    # Await terminations
    for session in sessions:
        session.wait_for_result()


def raw_image_path(image_id: str, device_id: str) -> str:
    return RAW_IMAGE_DIR + image_id + '_' + device_id


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


if __name__ == "__main__":
    # detect devices
    print('Discovering Raspberry PIs')
    ips = list(discover_pis(include_this_device=True))
    print('Found ' + str(ips))

    # connect to devices
    print('Connecting to ' + str(len(ips)) + ' devices.')
    connections = [connect_device(ip) for ip in ips]

    print('Making cameras ready for capturing')
    capture_sessions = [setup_for_capture(conn) for conn in connections]

    # TODO: Make this triggered by user
    time.sleep(1)  # allow raspistill to shut down
    print('Started capturing!')
    timestamp = datetime.datetime.now().isoformat()
    for session in capture_sessions:
        session.send_signal('SIGUSR1')

    print('Getting files from remote devices')
    time.sleep(1)
    for connection in connections:
        local_file_path = raw_image_path(timestamp, connection.cam_position)
        copy_remote_file(connection, TEMP_IMAGE_PATH, local_file_path)

    print('Generating GIF')
    image_paths = [raw_image_path(timestamp, conn.cam_position) for conn in connections]
    images = [imageio.imread(path) for path in image_paths]
    images_sequence = images[1:] + images[::-1][1:]  # [2, 3, 4, 3, 2, 1]
    gif_file_path = GIF_IMAGE_DIR + timestamp + '.gif'
    ensure_dir_exists(gif_file_path)
    imageio.mimwrite(gif_file_path, images_sequence, fps=8)
    print('Image successfully saved on disk as ' + gif_file_path)

    print('Ending session')
    end_sessions(capture_sessions)
