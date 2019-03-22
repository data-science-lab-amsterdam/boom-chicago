from sklearn.externals import joblib
import json

from src.standardize_images import main as standardize_image
from src.encoder import get_encoding
from src.pathfinder import Pathfinder

def main(image_dir, image_filename):
    output_dir = './storage_mount/images_start_cropped/'
    enc_start = get_encoding(image_dir + image_filename)
    enc_start = enc_start.reshape([1, len(enc_start)])

    if len(enc_start):
        standardize_image(image_dir, output_dir, image_filename)
        standardized_image_dir = output_dir + image_filename

        enc_pretty = joblib.load('./data/processed/face_encodings_pretty.pickle')
        enc_inter = joblib.load('./data/processed/face_encodings_inter.pickle')
        enc_ugly = joblib.load('./data/processed/face_encodings_ugly.pickle')

        img_filenames_pretty = joblib.load('./data/processed/image_filenames_pretty.pickle')
        img_filenames_inter = joblib.load('./data/processed/image_filenames_inter.pickle')
        img_filenames_ugly = joblib.load('./data/processed/image_filenames_ugly.pickle')

        pf = Pathfinder(enc_start, enc_inter, enc_pretty,
                        [output_dir + image_filename], img_filenames_inter, img_filenames_pretty,
                        'mixed'
                        )

        # idx_start needs to be removed as an index upon completion of the project
        path, distances = pf.find_path_from_start(idx_start=0, mode='closest', max_num_steps=10)

        json_string = json.dumps({'path': path, 'distances': distances})
        text = f'var data = {json_string};'

        with open('./src/www/path.js', 'w') as f:
            f.write(text)
    else:
        print('No face found in input image')

main(image_dir = '/Users/gijsromme/Downloads/', image_filename = 'cappy_test.jpg')