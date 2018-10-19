import datetime
import time

from flask import Flask, render_template, redirect, url_for
import imageio

import camera_ctrl
import img_utils

app = Flask(__name__)

RAW_IMAGE_DIR = 'static/OUTPUT/captured_raw/'
GIF_IMAGE_DIR = 'static/OUTPUT/captured_gifs/'


def raw_image_path(image_id: str, device_id: str) -> str:
    return RAW_IMAGE_DIR + image_id + '_' + device_id + '.jpg'


def initialize():
    """Prepare cameras for capturing"""

    # detect devices
    print('Discovering Raspberry PIs')
    # TODO: Automatic discovery is too unreliable, so IPs are hardcoded for now
    ips = ['172.20.10.14', '172.20.10.2', '172.20.10.3', '172.20.10.13']
    # ips = list(camera_ctrl.discover_pis(include_this_device=False))
    print('Found ' + str(ips))

    # connect to devices
    print('Connecting to ' + str(len(ips)) + ' devices.')
    connections = [camera_ctrl.connect_device(ip) for ip in ips]
    connections.sort(key=lambda conn: conn.cam_position)
    print('IPs sorted by cam position: ',
          [(conn.ip, conn.cam_position) for conn in connections])

    print('Making cameras ready for capturing')
    capture_sessions = [camera_ctrl.setup_for_capture(conn)
                        for conn in connections]

    return connections, capture_sessions


@app.route('/')
def show_start_screen():
    return render_template('start_screen.html')


@app.route('/add_contact_info/<gif_id>')
def show_add_contact_info(gif_id):
    return render_template('add_contact_info.html',
                           gif_id=gif_id)


@app.route('/store_info/<gif_id>/<contact_info>')
@app.route('/store_info/<gif_id>/')
def store_info(gif_id, contact_info=''):
    if contact_info != '':
        info_file_path = GIF_IMAGE_DIR + gif_id + '.txt'
        print('Storing contact info "' + contact_info + '" in ' + info_file_path)
        with open(info_file_path, 'w') as f:
            f.write(contact_info)
    else:
        print('No contact info provided')
    return redirect(url_for('show_start_screen'))


@app.route("/snap")
def snap_a_gif():
    """Take a gif photo"""

    print('Started capturing!')
    timestamp = datetime.datetime.now().isoformat()
    for session in capture_sessions:
        session.send_signal('SIGUSR1')
    time.sleep(0.5)  # give the camera time to store image on disk

    print('Getting files from remote devices')
    for connection in connections:
        local_file_path = raw_image_path(timestamp, connection.cam_position)
        camera_ctrl.copy_remote_file(connection,
                                     camera_ctrl.TEMP_IMAGE_PATH,
                                     local_file_path)

    print('Generating GIF')
    image_paths = [raw_image_path(timestamp, conn.cam_position)
                   for conn in connections]
    images = [imageio.imread(path) for path in image_paths]
    aligned_imgs = img_utils.auto_align(images)
    # [1, 2, 3, 4] -> [2, 3, 4, 3, 2, 1]
    images_sequence = aligned_imgs[1:] + aligned_imgs[::-1][1:]
    gif_id = timestamp
    gif_file_path = GIF_IMAGE_DIR + gif_id + '.gif'
    camera_ctrl.ensure_dir_exists(gif_file_path)
    imageio.mimwrite(gif_file_path, images_sequence, fps=8)
    print('Image successfully saved on disk as ' + gif_file_path)
    return redirect(url_for('show_add_contact_info',
                            gif_id=gif_id))


connections, capture_sessions = initialize()
app.run()
