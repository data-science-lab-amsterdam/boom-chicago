import numpy as np
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
import logging
import json


class Pathfinder:

    def __init__(self, encodings_start, encodings_inter, encodings_end,
                 filenames_start, filenames_inter, filenames_end,
                 distance_func='cosine'):
        self.op_counter = 0;
        self.encodings_start = encodings_start
        self.encodings_inter = encodings_inter
        self.encodings_end = encodings_end
        self.filenames_start = filenames_start
        self.filenames_inter = filenames_inter
        self.filenames_end = filenames_end

        if distance_func == 'cosine':
            self.distance_func = cosine_distances
        elif distance_func == 'euclidean':
            self.distance_func = euclidean_distances
        elif distance_func == 'mixed':
            self.distance_func = lambda X, Y: np.mean([cosine_distances(X, Y), euclidean_distances(X, Y)], axis=0)
        else:
            raise ValueError(f'Unknown distance function: {distance_func}')

        self.start_idx = None
        self.start_enc = None

    def get_start_image_index(self, filename):
        full_filename = 'data/' + filename
        return self.filenames_start.index(full_filename)

    def _set_start(self, idx):
        self.start_idx = idx
        self.start_enc = self._get_encoding(self.encodings_start, idx)

    def _get_encoding(self, encoding_matrix, idx):
        """ Extracts face encoding with row index 'idx' from 'enc_ndarray' and reshapes it to a usable size """
        return encoding_matrix[idx, :].reshape([1, len(encoding_matrix[idx, :])])

    def _get_closest_end_encoding(self):
        """ Finds the closest match from the photos in the "ugly" dataset with the starting photo and
        returns its encoding, index and the distance between the two photos """
        distances = self.distance_func(self.start_enc, self.encodings_end)
        idx_best = np.argmin(distances[0])
        end_enc = self._get_encoding(self.encodings_end, idx_best)
        return idx_best, end_enc

    def _evaluate_step(self, from_to_score, to_final_score, alpha=0.8):
        """ Returns a weighted average of the distance score between the photo from the previous step and one of the photos
        that can be chosen from in the current step (from_to_score) and the distance score between one of the current options and
        the destination photo (to_final_score). 'alpha' represents the weighting, with a higher alpha indicating a higher weight of
        the destination photo. """
        self.op_counter += 1
        return alpha * from_to_score + (1 - alpha) * to_final_score

    def _find_next_step(self, enc_from, enc_end, blacklist, alpha):
        """ Finds the next photo in the similarity path and returns its encoding (enc_next_step), index (idx_best)
        and the distance between it and the photo in the previous step.

        enc_from: encoding for the photo in the previous step
        enc_to_ndarray: ndarray containing all the encodings that can be chosen from in the current step on the rows
        enc_final: encoding for the final destination of the path
        distance_function: one of the sklearn functions 'cosine_distances', 'euclidean_distances' or 'manhattan_distances'
        alpha: weighting between 0 and 1 indicating the importance of the final destination of the path in finding the next photo in the path """

        distance_from_to_step = self.distance_func(enc_from, self.encodings_inter)[0]
        tmp = distance_from_to_step[distance_from_to_step > 0.]
        logging.info(f'Smallest distance: {tmp.min()}')
        distance_step_to_end = self.distance_func(enc_end, self.encodings_inter)[0]
        num_options = self.encodings_inter.shape[0]

        weighted_distances = [
            1. if i in blacklist else
            self._evaluate_step(distance_from_to_step[i], distance_step_to_end[i], alpha)
            for i in range(num_options)
        ]
        logging.info(f'Smallest weighed distance: {min(weighted_distances)}')

        idx_best = np.argmin(weighted_distances)
        enc_next_step = self._get_encoding(self.encodings_inter, idx_best)
        return idx_best, enc_next_step, distance_from_to_step[idx_best]

    def find_path_from_start(self, idx_start, mode='all', num_steps=5):
        self._set_start(idx_start)
        if mode == 'closest':
            idx_end, enc_end = self._get_closest_end_encoding()
            return self.find_path_from_start_to_end(idx_start, idx_end, num_steps=num_steps)
        elif mode == 'all':
            # try all options for end image
            pass
        else:
            raise ValueError(f'Invalid mode: {mode}')

    def find_path_from_start_to_end(self, idx_start, idx_end, num_steps=5):
        """ Finds the path between a photo from the input dataset with index 'starting_point_idx'
        distance_function: one of the sklearn functions 'cosine_distances', 'euclidean_distances' or 'manhattan_distances'
        num_steps: number of photos between the input photo and final destination photo """
        self.op_counter = 0

        # Let alpha decrease equidistantly from 1 to 0 between each of the steps
        alpha_list = np.arange(0, 1, 1 / (num_steps))[::-1]

        enc_from = self.start_enc
        enc_end = self._get_encoding(self.encodings_end, idx_end)
        distances = []
        path_idx = [idx_start]
        for i in range(num_steps):
            # update alpha value
            alpha = alpha_list[i]

            # find next step
            idx_next, enc_next, distance = self._find_next_step(enc_from, enc_end, blacklist=path_idx, alpha=alpha)

            # Store obtained results
            distances.append(distance)
            path_idx.append(idx_next)

            # update the current 'from' encoding
            enc_from = enc_next.copy()

        # Photo filenames per step for respective datasets
        path_images = []
        for i, value in enumerate(path_idx):
            if i == 0:
                path_images.append(self.filenames_start[value])
            else:
                path_images.append(self.filenames_inter[value])
        path_images.append(self.filenames_end[idx_end])

        total_distance = self.distance_func(enc_from, enc_end)

        logging.info(path_images)
        logging.info(f'{self.op_counter} steps taken')
        logging.info(f'Distance from start to end: {total_distance}')
        logging.info(f'Mean distance: {np.mean(distances)}')
        logging.info(f'Highest distance: {np.max(distances)}')
        return path_images, distances


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

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
                    'cosine'
                    )

    path, distances = pf.find_path_from_start(idx_start=12, mode='closest', num_steps=7)

    json_string = json.dumps({'path': path, 'distances': distances})
    text = f'var data = {json_string};'

    with open('./src/www/path.js', 'w') as f:
        f.write(text)
