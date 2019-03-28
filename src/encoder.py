import numpy as np
from tqdm import tqdm
import face_recognition
from pathlib import Path
from sklearn.externals import joblib
import logging


def get_encoding(filename, margin=0):

    # load the image
    img_rgb = face_recognition.load_image_file(filename)

    # detect faces
    face_locations = face_recognition.face_locations(img_rgb)
    if not face_locations:
        logging.error(f'No face found in image {filename}')
        face_encoding = np.zeros(128)
    else:
        if margin > 0:
            face_locations = [
                (t-margin, r+margin, b+margin, l-margin) for (t, r, b, l) in face_locations
            ]
        # get face encoding (of 1st face found in image)
        face_encoding = face_recognition.face_encodings(img_rgb, known_face_locations=face_locations)[0]

    return face_encoding


def get_encodings_ndarray(filenames):
    encodings = np.zeros((len(filenames), 128))  # encodings have size 128
    i = -1
    for filename in tqdm(filenames):  # tqdm displays a progress bar
        i += 1
        encodings[i, :] = get_encoding(filename)
    return encodings


def get_files(path, patterns):
    """
    Get a list of all filenames in a certain path with allowed extensions
    """
    files = []
    for p in patterns:
        files.extend(Path(path).rglob(p))
    return files


def main(subset):
    for namepart in subset:
        dirname = f'images_{namepart}'
        if namepart in ['pretty', 'ugly']:
            dirname = f'images_end_{namepart}_cropped'

        img_filenames = [str(f) for f in get_files(f'./storage_mount/{dirname}', ['*.jpg', '*.jpeg', '*.png'])]
        encodings = get_encodings_ndarray(img_filenames)
        joblib.dump(img_filenames, f'./data/processed/image_filenames_{namepart}.pickle')
        joblib.dump(encodings, f'./data/processed/face_encodings_{namepart}.pickle')


if __name__ == '__main__':
    #main(subset=['start', 'intermediate', 'pretty', 'ugly'])
    main(subset=['pretty', 'ugly'])
