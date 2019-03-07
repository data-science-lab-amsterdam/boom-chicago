import numpy as np
import pandas as pd
from tqdm import tqdm
import face_recognition
from pathlib import Path
from sklearn.externals import joblib
import logging


def get_encodings(filenames):
    encodings = np.zeros((len(filenames), 128))  # encodings have size 128
    i = -1
    for filename in tqdm(filenames):  # tqdm displays a progress bar
        i += 1
        # load the image
        img_rgb = face_recognition.load_image_file(filename)

        # detect faces
        face_locations = face_recognition.face_locations(img_rgb)
        if not face_locations:
            logging.error(f'No face found in image {filename}')
            continue

        # get face encoding (of 1st face found in image)
        face_encoding = face_recognition.face_encodings(img_rgb, known_face_locations=face_locations)[0]

        encodings[i, :] = face_encoding

    return encodings


images_start = list(Path('./data/images_start').glob('*.jpg'))
images_inter = list(Path('./data/images_intermediate').glob('*.jpg'))
images_pretty = list(Path('./data/images_end_pretty').glob('*.jpg'))
images_ugly = list(Path('./data/images_end_ugly').glob('*.jpg'))

img_filenames_start = list(map(str, images_start))
img_filenames_inter = list(map(str, images_inter))
img_filenames_pretty = list(map(str, images_pretty))
img_filenames_ugly = list(map(str, images_ugly))

encodings_start = get_encodings(images_start)
encodings_inter = get_encodings(images_inter)
encodings_pretty = get_encodings(images_pretty)
encodings_ugly = get_encodings(images_ugly)

# save to disk
joblib.dump(img_filenames_start, './data/processed/image_filenames_start.pickle')
joblib.dump(img_filenames_inter, './data/processed/image_filenames_inter.pickle')
joblib.dump(img_filenames_pretty, './data/processed/image_filenames_pretty.pickle')
joblib.dump(img_filenames_ugly, './data/processed/image_filenames_ugly.pickle')
joblib.dump(encodings_start, './data/processed/face_encodings_start.pickle')
joblib.dump(encodings_inter, './data/processed/face_encodings_inter.pickle')
joblib.dump(encodings_pretty, './data/processed/face_encodings_pretty.pickle')
joblib.dump(encodings_ugly, './data/processed/face_encodings_ugly.pickle')



