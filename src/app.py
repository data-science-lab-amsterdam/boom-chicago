from flask import Flask, render_template, url_for, send_from_directory, request, redirect, session
from pathlib import Path
from sklearn.externals import joblib
import json
from werkzeug.utils import secure_filename
import logging
import sys
sys.path.append('./src')

from pathfinder import Pathfinder
import encoder
import standardize_images


logging.basicConfig(level=logging.INFO)


PATHFINDER_DISTANCE_FUNC = 'cosine'
PATHFINDER_END_MODE = 'closest'
PATHFINDER_PATH_LENGTH = 8


def get_files(path, patterns):
    """
    Get a list of all filenames in a certain path with allowed extensions
    """
    files = []
    for p in patterns:
        files.extend(Path(path).rglob(p))
    return files


def get_start_images():
    """
    Retrieve path and name of all starting images to choose from
    """
    files = get_files('./storage_mount/images_start', ['*.jpg', '*.png', '*.jpeg'])

    def _get_name(path):
        return Path(path).name.split("-")[0]

    def _get_subpath(path):
        return '/'.join(str(path).split('/')[1:])

    return [{'url': _get_subpath(filename), 'name': _get_name(filename)} for filename in files]


def get_uploaded_image(filename):
    return {'url': "images_start/"+filename, 'name': Path(filename).name.split("-")[0]}


def get_pathfinder(distance_func='mixed', end='ugly'):
    """
    Initialize a pathfinder using pre-defined image encodings
    """
    # load face encodings
    enc_start = joblib.load('./data/processed/face_encodings_start.pickle')
    # enc_inter = joblib.load('./data/processed/face_encodings_intermediate.pickle')
    enc_inter = joblib.load('./data/processed/face_encodings_stylegan.pickle')
    enc_pretty = joblib.load('./data/processed/face_encodings_pretty.pickle')
    enc_ugly = joblib.load('./data/processed/face_encodings_ugly.pickle')

    # load file names
    img_filenames_start = joblib.load('./data/processed/image_filenames_start.pickle')
    # img_filenames_inter = joblib.load('./data/processed/image_filenames_intermediate.pickle')
    img_filenames_inter = joblib.load('./data/processed/image_filenames_stylegan.pickle')
    img_filenames_pretty = joblib.load('./data/processed/image_filenames_pretty.pickle')
    img_filenames_ugly = joblib.load('./data/processed/image_filenames_ugly.pickle')

    pf = Pathfinder(enc_start,
                    enc_inter,
                    (enc_pretty if end == 'pretty' else enc_ugly),
                    img_filenames_start,
                    img_filenames_inter,
                    (img_filenames_pretty if end == 'pretty' else img_filenames_ugly),
                    distance_func
                    )
    return pf


def process_image(filename):
    """
    Process an uploaded image so it can be used in the app
    """
    # crop image
    logging.info("standardizing image...")
    standardize_images.main('./storage_mount/images_upload', './storage_mount/images_start', filename)

    # add to encodings & filenames
    logging.info("refreshing start encodings...")
    encoder.main(subset=['start'])

    refresh_pathfinders()


def refresh_pathfinders():
    """
    After encodings & filenames have been updated, the pathfinder needs to refresh them
    """
    global pathfinder_pretty, pathfinder_ugly
    pathfinder_pretty = get_pathfinder(distance_func=PATHFINDER_DISTANCE_FUNC, end='pretty')
    pathfinder_ugly = get_pathfinder(distance_func=PATHFINDER_DISTANCE_FUNC, end='ugly')


app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['UPLOAD_FOLDER'] = "./storage_mount/images_upload"

pathfinder_pretty = get_pathfinder(distance_func=PATHFINDER_DISTANCE_FUNC, end='pretty')
pathfinder_ugly = get_pathfinder(distance_func=PATHFINDER_DISTANCE_FUNC, end='ugly')


@app.route("/")
def register():
    """
    Render the registration page
    """
    return render_template('register.html')


@app.route("/admin")
def admin():
    """
    Render the admin page and pass along starting images
    """
    data = {
        'starting_images': [item for item in get_start_images()]
    }
    return render_template('admin.html', data=data)


@app.route("/upload")
def upload():
    """
    Render the page where the user can upload his photo
    """
    return render_template('upload.html')


@app.route("/show-path", methods=['POST'])
def show_path():
    try:
        file = request.files['photo']
        filename = secure_filename(file.filename)
        logging.info(filename)
        internal_path = str(Path(app.config['UPLOAD_FOLDER']) / filename)
        file.save(internal_path)

        process_image(filename)

        data = {
            'image': get_uploaded_image(filename)
            # 'image': get_start_images()[0]
        }
        return render_template('show-path.html', data=data)
    except Exception as e:
        logging.error(e)
        return redirect(url_for('upload'), code=406)


@app.route('/images/<path:path>')
def serve_images(path):
    """
    Pass local images to the web server
    """
    return send_from_directory(directory=Path.cwd() / 'storage_mount', filename=path)


@app.route('/get_results', methods=['GET'])
def get_results():
    """
    Given a starting image, find a path along similar images towards a final image
    """
    image_path = request.args.get('image')
    logging.info(image_path)

    idx_start = pathfinder_ugly.get_start_image_index(image_path)
    ugly_path, ugly_distances = pathfinder_ugly.find_path_from_start(
        idx_start=idx_start,
        mode=PATHFINDER_END_MODE,
        max_num_steps=PATHFINDER_PATH_LENGTH
    )
    ugly_path = [p.replace('storage_mount/', '') for p in ugly_path]

    pretty_path, pretty_distances = pathfinder_pretty.find_path_from_start(
        idx_start=idx_start,
        mode=PATHFINDER_END_MODE,
        max_num_steps=PATHFINDER_PATH_LENGTH
    )
    pretty_path = [p.replace('storage_mount/', '') for p in pretty_path]

    data = {
        'ugly': {
            'path': ugly_path,
            'distances': ugly_distances
        },
        'pretty': {
            'path': pretty_path,
            'distances': pretty_distances
        }
    }
    return json.dumps(data)


@app.route('/update_image_encodings', methods=['GET'])
def update_image_encodings():
    try:
        encoder.main(subset=['start'])
        return json.dumps(True)
    except Exception:
        return json.dumps(False)


if __name__ == '__main__':
    app.run()
