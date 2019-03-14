from flask import Flask, render_template, url_for, send_from_directory, request
from pathlib import Path
from sklearn.externals import joblib
import json
import logging

from pathfinder import Pathfinder


logging.basicConfig(level=logging.INFO)


def get_start_images():
    files = Path('./data/images_start').glob('*')

    def _get_name(path):
        return Path(path).name.split("-")[0]

    def _get_subpath(path):
        return '/'.join(str(path).split('/')[1:])

    return [{'url': _get_subpath(filename), 'name': _get_name(filename)} for filename in files]


def get_pathfinder(distance_func='mixed'):
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

    pf = Pathfinder(enc_start, enc_inter, enc_pretty,
                    img_filenames_start, img_filenames_inter, img_filenames_pretty,
                    distance_func
                    )
    return pf


app = Flask(__name__, static_folder='static', template_folder='templates')

pathfinder = get_pathfinder(distance_func='cosine')


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
    return send_from_directory(directory=Path.cwd() / 'data', filename=path)


@app.route('/get_results', methods=['GET'])
def get_results():
    """
    Given a starting image, find a path along similar images towards a final image
    """
    image_path = request.args.get('image')
    logging.info(image_path)

    idx_start = pathfinder.get_start_image_index(image_path)
    path, distances = pathfinder.find_path_from_start(idx_start=idx_start, mode='closest', num_steps=5)

    # data = {
    #     'path': [
    #         "images_start/Demi-2-300x300.jpg", "images_intermediate/Elizabeth_Berkeley_0001.jpg",
    #         "images_intermediate/Mona_Rishmawi_0001.jpg", "images_intermediate/Alexandra_Pelosi_0001.jpg",
    #         "images_intermediate/Catherine_Donkers_0001.jpg", "images_intermediate/Erin_Runnion_0001.jpg",
    #         "images_intermediate/Xiang_Huaicheng_0001.jpg"
    #     ],
    #     'similarities': [1, 2, 3, 4, 5, 6]
    # }
    data = {
        'path': [p.replace('data/', '') for p in path],
        'distances': distances
    }
    return json.dumps(data)


if __name__ == '__main__':
    app.run()
