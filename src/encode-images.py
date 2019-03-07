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

img_filenames = list(map(str, images_start + images_inter + images_pretty))

encodings_start = get_encodings(images_start)
encodings_inter = get_encodings(images_inter)
encodings_pretty = get_encodings(images_pretty)

all = np.vstack([encodings_start, encodings_inter, encodings_pretty])

all.shape

# save to disk
joblib.dump(img_filenames, './data/processed/image_filenames.pickle')
joblib.dump(all, './data/processed/face_encodings.pickle')



