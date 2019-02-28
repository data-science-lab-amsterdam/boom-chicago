import numpy as np


ALPHA = 0.8
NUM_ITEMS = 10000
# suppose this is a N x N matrix of similarities (pre-computed)
# yes it should be symmetrical but it doesn't matter 'cause we only lookup via the same indices
sim = np.random.rand(NUM_ITEMS, NUM_ITEMS)

# counter to check how many computations are needed
num_sim_steps = 0


def evaluate_step(a, z, k):
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
    return ALPHA * sim[a, k] + (1-ALPHA) * sim[k, z]


def find_path(start=0, end=1, num_steps=5):
    global num_sim_steps
    num_sim_steps = 0

    path = [start]
    for step in range(num_steps):
        current = path[-1]
        candidates = [i for i in range(NUM_ITEMS) if i not in path + [end]]
        idx_best = np.argmax([evaluate_step(current, end, c) for c in candidates])
        path.append(candidates[idx_best])
    path.append(end)

    print(path)
    print(f'{num_sim_steps} steps')
    return path


find_path(start=0, end=99, steps=5)
