from flask import Flask, render_template, redirect, url_for

import camera_master


app = Flask(__name__)

GIF_IMAGE_DIR = 'static/OUTPUT/'


@app.route('/')
def show_start_screen():
    return render_template('start_screen.html')


@app.route("/snap")
def snap_a_gif():
    gif_file_path = camera_master.take_photo()
    return redirect(url_for('show_add_contact_info', gif_id=gif_file_path))


@app.route('/add_contact_info/<gif_id>')
def show_add_contact_info(gif_id):
    return render_template('add_contact_info.html', gif_id=gif_id)


@app.route('/store_info/<gif_id>/<contact_info>')
@app.route('/store_info/<gif_id>/')
def store_info(gif_id, contact_info=''):
    if contact_info != '':
        info_file_path = GIF_IMAGE_DIR + gif_id + '.txt'
        print('Storing contact info "' + contact_info + '" in ' +
              info_file_path)
        with open(info_file_path, 'w') as f:
            f.write(contact_info)
    else:
        print('No contact info provided')
    return redirect(url_for('show_start_screen'))


app.run()
