"""
Thanks to nallic for providing a big portion of this code at
https://github.com/nallic/pi3dscanner/
"""

import time
import shutil
import datetime

import nmap
import spur
import imageio


HOSTS = '172.20.10.0/24'  # for iOS 6 and 7
DEFAULT_USERNAME = 'pi'
DEFAULT_PASSWORD = 'raspberry'
TEMP_IMAGE_PATH = '/tmp/wobble_gif_cam/latest.jpg'
RAW_IMAGE_DIR = 'wobble_gif_cam/captured_raw/'
GIF_IMAGE_DIR = 'wobble_gif_cam/captured_gif/'
JPEG_QUALITY = '99'


def discover_pis() -> [str]:
    ips = []
    nm = nmap.PortScanner()
    scan = nm.scan(hosts=HOSTS, arguments='-sn', sudo=True)
    for unit_ip, unit_values in scan['scan'].items():
        try:
            if next(iter(unit_values['vendor'].values())) in 'Raspberry Pi Foundation':
                ips.append(unit_ip)
        except StopIteration:  # TODO: WTF!?
            pass  # ignore results without MAC
    return ips


def connect_device(ip: str, ident: str) -> spur.ssh.SshShell:
    print('connecting to ' + ip)
    shell = spur.SshShell(hostname=ip, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD,
                          missing_host_key=spur.ssh.MissingHostKey.accept)
    cam_position = shell.run(['echo', '$WOBBLE_GIF_CAM_POSITION'])
    shell.cam_position = cam_position
    return shell


def end_sessions(sessions: [spur.ssh.SshProcess]) -> None:
    for session in sessions:
        session.send_signal('SIGUSR2')

    # Await terminations
    for session in sessions:
        session.wait_for_result()


def raw_image_path(image_id: str, device_id: str) -> str:
    return RAW_IMAGE_DIR + image_id + ' ' + device_id


def setup_for_capture(connection) -> spur.ssh.SshProcess:
    # cleanup all devices
    # connection.run(['killall', '-w', '-s', 'USR2', 'raspistill'], allow_error=True)  # kill old sessions
    # connection.run(['rm', '-rf', gen_filepath(session_name)], allow_error=True)  # remove old session with same name
    # connection.run(['mkdir', gen_filepath(session_name)])  # create folder for captures
    # start raspistill
    print('Connecting to ' + connection.ident)
    file_path = connection.ident + '.jpg'
    raspistill_process = connection.spawn(['raspistill', '-o', file_path, '-dt', '-t', '0', '-q', JPEG_QUALITY, '-s'], store_pid=True)
    return raspistill_process


def copy_remote_file(connection: spur.ssh.SshShell, remote_file_path: str, local_file_path: str) -> None:
    print('Copying ' + TEMP_IMAGE_PATH + ' from REMOTE ' + connection.ident + ' to ' + local_file_path + ' locally.')
    with connection.open(remote_file_path, "rb") as remote_file:
        with open(local_file_path, "wb") as local_file:
            shutil.copyfileobj(remote_file, local_file)


if __name__ == "__main__":
    print('Discovering Raspberry PIs')

    # detect devices
    ips = discover_pis()

    # connect to devices
    print('Initializing. Connecting to ' + str(len(ips)) + ' devices.')
    connections = [connect_device(ip, 'device' + str(index)) for index, ip in enumerate(ips)]

    print('setting up capture environment')
    capture_sessions = [setup_for_capture(conn) for conn in connections]
    print('waiting for devices to settle')
    time.sleep(1)  # allow raspistill to shut down

    print('started capturing!')
    timestamp = datetime.datetime.now().isoformat()
    for session in capture_sessions:
        session.send_signal('SIGUSR1')
    time.sleep(1)

    print('Getting files from remote devices')
    for connection in connections:
        copy_remote_file(connection, TEMP_IMAGE_PATH, raw_image_path(timestamp, connection.ident))

    print('Generating GIF')
    image_paths = [raw_image_path(timestamp, conn.ident) for conn in connections]
    images = [imageio.imread() for path in image_paths]
    images_sequence = images[1:] + images[::-1][1:]  # [2, 3, 4, 3, 2, 1]
    imageio.mimwrite(GIF_IMAGE_DIR + timestamp + '.gif', images_sequence, fps=8)
    print('Image successfully saved on disk in ' + GIF_IMAGE_DIR)

    print('Ending session')
    end_sessions(capture_sessions)
