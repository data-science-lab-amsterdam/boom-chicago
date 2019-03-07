import numpy as np
import pandas as pd
from sklearn.externals import joblib
from sklearn.metrics.pairwise import cosine_similarity
import json

ALPHA = 0.8

# counter to check how many computations are needed
num_sim_steps = 0


def evaluate_step(a, z, k, alpha=0.8):
    """
    Evaluate how good k is when wanting to go from a to z
    What we want to maximise is
    - high similarity between a & k (so the direct match a-k works)
    - high similarity between z & k (so it's be easier to go from k to z)
    """
    global num_sim_steps
    num_sim_steps += 1
    if a == k or z == k:
        return -1
    return alpha * sim[a, k] + (1-alpha) * sim[k, z]


def find_path(start=0, end=1, num_items=10, num_steps=5, alpha=0.8):
    global num_sim_steps
    num_sim_steps = 0

    path = [start]
    similarities = []
    for step in range(num_steps):
        current = path[-1]
        candidates = [i for i in range(num_items) if i not in path + [end]]
        idx_best = np.argmax([evaluate_step(current, end, c, alpha) for c in candidates])
        path.append(candidates[idx_best])
        similarities.append(sim[current, candidates[idx_best]])
    path.append(end)

    print(path)
    print(f'{num_sim_steps} steps taken')
    print(f'Total similarity start to end: {sim[start, end]}')
    print(f'Mean similarity: {np.mean(similarities)}')
    print(f'Lowest similarity: {np.min(similarities)}')
    return path, similarities


enc = joblib.load('./data/processed/face_encodings.pickle')

sim = cosine_similarity(enc, enc)

sim.shape


# suppose this is a N x N matrix of similarities (pre-computed)
# yes it should be symmetrical but it doesn't matter 'cause we only lookup via the same indices
#sim = np.random.rand(NUM_ITEMS, NUM_ITEMS)

num_items = sim.shape[0]
path, similarities = find_path(start=0, end=5730, num_items=num_items, num_steps=5, alpha=ALPHA)

# load file names
img_filenames = joblib.load('./data/processed/image_filenames.pickle')


def get_images_from_path(path):
    path_files = [img_filenames[i] for i in path]
    return path_files


path_images = get_images_from_path(path)

json_string = json.dumps(path_images)
text = f'var images = {json_string};'

with open('./src/www/path.js', 'w') as f:
    f.write(text)
