import numpy as np
from tqdm import tqdm
import face_recognition
from pathlib import Path
from sklearn.externals import joblib
import logging


def get_encoding(filename):

    # load the image
    img_rgb = face_recognition.load_image_file(filename)

    # detect faces
    face_locations = face_recognition.face_locations(img_rgb)
    if not face_locations:
        logging.error(f'No face found in image {filename}')
        face_encoding = []
    else:
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
        files.extend(Path(path).glob(p))
    return files

def main():
    images_start = list(get_files('./storage_mount/images_start', ['*.jpg', '*.jpeg', '*.png']))
    images_inter = list(get_files('./storage_mount/images_intermediate', ['*.jpg', '*.jpeg', '*.png']))
    images_pretty = list(get_files('./storage_mount/images_end_pretty_cropped', ['*.jpg', '*.jpeg', '*.png']))
    images_ugly = list(get_files('./storage_mount/images_end_ugly_cropped', ['*.jpg', '*.jpeg', '*.png']))

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


if __name__ == '__main__':
    main()

