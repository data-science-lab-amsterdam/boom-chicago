import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances, manhattan_distances
from face_recognition.api import face_distance
import json

ALPHA = 0.8

# counter to check how many computations are needed
num_sim_steps = 0

enc_start = joblib.load('./data/processed/face_encodings_start.pickle')
enc_pretty = joblib.load('./data/processed/face_encodings_pretty.pickle')
enc_inter = joblib.load('./data/processed/face_encodings_inter.pickle')
enc_ugly = joblib.load('./data/processed/face_encodings_ugly.pickle')

# load file names
img_filenames_start = joblib.load('./data/processed/image_filenames_start.pickle')
img_filenames_pretty = joblib.load('./data/processed/image_filenames_pretty.pickle')
img_filenames_inter = joblib.load('./data/processed/image_filenames_inter.pickle')
img_filenames_ugly = joblib.load('./data/processed/image_filenames_ugly.pickle')


def extract_face_encoding(enc_ndarray, idx):
    ''' Extracts face encoding with row index 'idx' from 'enc_ndarray' and reshapes it to a usable size '''
    return enc_ndarray[idx, :].reshape([1, len(enc_ndarray[idx, :])])

def find_destination_encoding(enc_from, distance_function):
    ''' Finds the closest match from the photos in the "ugly" dataset with the starting photo and
    returns its encoding, index and the distance between the two photos '''
    distance = distance_function(enc_from, enc_ugly)
    idx_best = np.argmin(distance[0])
    enc_destination = extract_face_encoding(enc_ugly, idx_best)
    return enc_destination, distance[0][idx_best], idx_best

def evaluate_step(from_to_score, to_final_score, alpha=0.8):
    ''' Returns a weighted average of the distance score between the photo from the previous step and one of the photos
    that can be chosen from in the current step (from_to_score) and the distance score between one of the current options and
    the destination photo (to_final_score). 'alpha' represents the weighting, with a higher alpha indicating a higher weight of
    the destination photo. '''
    global num_sim_steps
    num_sim_steps += 1
    return alpha * from_to_score + (1-alpha) * to_final_score

def find_next_step_encoding(enc_from, enc_to_ndarray, enc_final, distance_function, alpha):
    ''' Finds the next photo in the similarity path and returns its encoding (enc_next_step), index (idx_best)
    and the distance between it and the photo in the previous step.

    enc_from: encoding for the photo in the previous step
    enc_to_ndarray: ndarray containing all the encodings that can be chosen from in the current step on the rows
    enc_final: encoding for the final destination of the path
    distance_function: one of the sklearn functions 'cosine_distances', 'euclidean_distances' or 'manhattan_distances'
    alpha: weighting between 0 and 1 indicating the importance of the final destination of the path in finding the next photo in the path '''

    distance_from_to = distance_function(enc_from, enc_to_ndarray)[0]
    distance_to_final = distance_function(enc_final, enc_to_ndarray)[0]
    num_options = enc_to_ndarray.shape[0]

    weighted_distances = [evaluate_step(distance_from_to[i], distance_to_final[i], alpha) for i in range(num_options)]
    idx_best = np.argmin(weighted_distances)
    enc_next_step = extract_face_encoding(enc_to_ndarray, idx_best)
    return enc_next_step, weighted_distances[idx_best], idx_best

def find_path(starting_point_idx, distance_function, num_steps = 3):
    ''' Finds the path between a photo from the input dataset with index 'starting_point_idx'
    distance_function: one of the sklearn functions 'cosine_distances', 'euclidean_distances' or 'manhattan_distances'
    num_steps: number of photos between the input photo and final destination photo '''

    # Score to keep track of how many computations were made in total
    global num_sim_steps
    num_sim_steps = 0
    # Let alpha increase equidistantly from 0 to 1 between each of the steps
    alpha_list = np.arange(0, 1, 1/(num_steps))

    # Extract encoding for starting point
    enc_from = extract_face_encoding(enc_start, 11)
    # Find encoding for best destination
    enc_final, total_distance, destination_idx = find_destination_encoding(enc_from, distance_function)
    # Manual selection of destination photo
    # enc_final, total_distance, destination_idx = extract_face_encoding(enc_ugly, 7), 1, 7

    distances = []
    steps_idxs = []
    for i in range(num_steps):
        alpha = alpha_list[i]
        if i == 0:
            enc_to_ndarray = enc_pretty
        elif i == 1:
            enc_to_ndarray = enc_inter
        elif i >= 2:
            # Remove encodings of photos that were already used from the selection pool
            enc_to_ndarray = np.vstack([enc_to_ndarray[:end_idx, :] , enc_to_ndarray[end_idx+1:, :]])

        # Get encoding to use in the next round
        enc_from, distance, end_idx = find_next_step_encoding(enc_from, enc_to_ndarray, enc_final, distance_function, alpha)
        # Store obtained results
        distances.append(distance)
        steps_idxs.append(end_idx)

    # Photo filenames per step for respective datasets
    path = [img_filenames_start[starting_point_idx]]
    for i in range(num_steps):
        if i == 0:
            path += [img_filenames_pretty[steps_idxs[i]]]
        elif i >= 1:
            path += [img_filenames_inter[steps_idxs[i]]]
    path += [img_filenames_ugly[destination_idx]]

    print(path)
    print(f'{num_sim_steps} steps taken')
    print(f'Distance from start to end: {total_distance}')
    print(f'Mean distance: {np.mean(distances)}')
    print(f'Highest distance: {np.max(distances)}')
    return path, distances

# ----------------------------------------------------------------------------------------------------------------------------------

starting_point_idx = 11
# Choose distance functions from: cosine_distances, euclidean_distances, manhattan_distances
path_images, distances = find_path(starting_point_idx, cosine_distances, num_steps=5)

json_string = json.dumps(path_images)
text = f'var images = {json_string};'

with open('./src/www/path.js', 'w') as f:
    f.write(text)
