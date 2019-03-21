from flask import Flask, render_template, url_for, send_from_directory, request
from pathlib import Path
from sklearn.externals import joblib
import json
import logging
import sys
sys.path.append('./src')
from pathfinder import Pathfinder


logging.basicConfig(level=logging.INFO)


PATHFINDER_DISTANCE_FUNC = 'mixed'
PATHFINDER_END_MODE = 'closest'
PATHFINDER_PATH_LENGTH = 4


def get_start_images():
    """
    Retrieve path and name of all starting images to choose from
    """
    files = Path('./storage_mount/images_start').glob('*')

    def _get_name(path):
        return Path(path).name.split("-")[0]

    def _get_subpath(path):
        return '/'.join(str(path).split('/')[1:])

    return [{'url': _get_subpath(filename), 'name': _get_name(filename)} for filename in files]


def get_pathfinder(distance_func='mixed', end='ugly'):
    """
    Initialize a pathfinder using pre-defined image encodings
    """
    # load face encodings
    enc_start = joblib.load('./data/processed/face_encodings_start.pickle')
    enc_pretty = joblib.load('./data/processed/face_encodings_pretty.pickle')
    enc_inter = joblib.load('./data/processed/face_encodings_inter.pickle')
    enc_ugly = joblib.load('./data/processed/face_encodings_ugly.pickle')

    # load file names
    img_filenames_start = joblib.load('./data/processed/image_filenames_start.pickle')
    img_filenames_pretty = joblib.load('./data/processed/image_filenames_pretty.pickle')
    img_filenames_inter = joblib.load('./data/processed/image_filenames_inter.pickle')
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


app = Flask(__name__, static_folder='static', template_folder='templates')

pathfinder_pretty = get_pathfinder(distance_func=PATHFINDER_DISTANCE_FUNC, end='pretty')
pathfinder_ugly = get_pathfinder(distance_func=PATHFINDER_DISTANCE_FUNC, end='ugly')


@app.route("/")
def home():
    """
    Render the homepage and pass along starting images
    """
    data = {
        'starting_images': [item for item in get_start_images()]
    }
    return render_template('index.html', data=data)


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
        num_steps=PATHFINDER_PATH_LENGTH
    )
    ugly_path = [p.replace('storage_mount/', '') for p in ugly_path]

    pretty_path, pretty_distances = pathfinder_pretty.find_path_from_start(
        idx_start=idx_start,
        mode=PATHFINDER_END_MODE,
        num_steps=PATHFINDER_PATH_LENGTH
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
    import encoder
    try:
        encoder.main()
        return json.dumps(True)
    except Exception:
        return False


if __name__ == '__main__':
    app.run()
