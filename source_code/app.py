import time
import datetime
from flask import Flask

import imageio
import camera_ctrl

app = Flask(__name__)


def initialize():
    """Prepare cameras for capturing"""

    # detect devices
    print('Discovering Raspberry PIs')
    ips = list(camera_ctrl.discover_pis(include_this_device=False))
    print('Found ' + str(ips))

    # connect to devices
    print('Connecting to ' + str(len(ips)) + ' devices.')
    connections = [camera_ctrl.connect_device(ip) for ip in ips]
    connections.sort(key=lambda conn: conn.cam_position)

    print('Making cameras ready for capturing')
    capture_sessions = [camera_ctrl.setup_for_capture(conn) for conn in connections]

    return connections, capture_sessions


@app.route("/snap")
def snap_a_gif():
    """Take a gif photo"""

    print('Started capturing!')
    timestamp = datetime.datetime.now().isoformat()
    for session in capture_sessions:
        session.send_signal('SIGUSR1')

    print('Getting files from remote devices')
    time.sleep(1)
    for connection in connections:
        local_file_path = camera_ctrl.raw_image_path(timestamp, connection.cam_position)
        camera_ctrl.copy_remote_file(connection, camera_ctrl.TEMP_IMAGE_PATH, local_file_path)

    print('Generating GIF')
    image_paths = [camera_ctrl.raw_image_path(timestamp, conn.cam_position) for conn in connections]
    images = [imageio.imread(path) for path in image_paths]
    images_sequence = images[1:] + images[::-1][1:]  # [2, 3, 4, 3, 2, 1]
    gif_file_path = camera_ctrl.GIF_IMAGE_DIR + timestamp + '.gif'
    camera_ctrl.ensure_dir_exists(gif_file_path)
    imageio.mimwrite(gif_file_path, images_sequence, fps=8)
    print('Image successfully saved on disk as ' + gif_file_path)

    return 'Image successfully saved on disk as ' + gif_file_path


connections, capture_sessions = initialize()
app.run()
