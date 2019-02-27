import numpy as np
import pandas as pd
from tqdm import tqdm
import face_recognition
from pathlib import Path
from sklearn.externals import joblib
import logging


# some list of filenames (create with glob or something)
images = []

X = np.zeros((len(images), 128))  # encodings have size 128
i = -1
for filename in tqdm(images):  # tqdm displays a progress bar
    i += 1
    # load the image
    full_path = Path('./data/raw') / filename
    img_rgb = face_recognition.load_image_file(full_path)

    # detect faces
    face_locations = face_recognition.face_locations(img_rgb)
    if not face_locations:
        logging.error(f'No face found in image {filename}')
        continue

    # get face encoding (of 1st face found in image)
    face_encoding = face_recognition.face_encodings(img_rgb, known_face_locations=face_locations)[0]

    X[i, :] = face_encoding


# save to disk
joblib.dump(X, './data/processed/face_encodings.pickle')

