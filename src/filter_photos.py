from scipy.spatial.distance import euclidean
import face_recognition
import operator
import numpy as np
import os

img_dir = './storage_mount/images_intermediate_pexels/'
photo_names_list = [file for file in os.listdir(img_dir) if not file.startswith('.DS')]

# img = './storage_mount/images_intermediate_pexels/678783.jpg'
# image = face_recognition.load_image_file(img)
# landmarks1 = face_recognition.face_landmarks(img_rgb, model = 'small')
#
# img2 = './storage_mount/images_intermediate_pexels/1376048.jpg'
# img_rgb2 = face_recognition.load_image_file(img2)
# landmarks2 = face_recognition.face_landmarks(img_rgb2, model = 'small')
#
# face_part1 = 'right_eye'
# face_part2 = 'left_eye'
# (landmarks1[0][face_part1][1][0] - landmarks1[0][face_part1][0][0], landmarks1[0][face_part2][1][1] - landmarks1[0][face_part2][0][1])
# (landmarks2[0][face_part1][1][0] - landmarks2[0][face_part1][0][0], landmarks2[0][face_part2][1][1] - landmarks2[0][face_part2][0][1])

def euc_distance(landmarks):
    return (euclidean(landmarks[0]['left_eye'][0], landmarks[0]['left_eye'][1])/ euclidean(landmarks[0]['right_eye'][1], landmarks[0]['right_eye'][0]))
    # return (euclidean(landmarks[0]['right_eye'][0], landmarks[0]['left_eye'][1])/ euclidean(tuple(map(operator.add, landmarks[0]['left_eye'][1], landmarks[0]['right_eye'][0])), landmarks[0]['nose_tip'][0]))

# (euclidean(landmarks2[0]['nose_tip'][0], landmarks2[0]['left_eye'][1]), euclidean(landmarks2[0]['right_eye'][0], landmarks2[0]['nose_tip'][0]))
#
# # Find the location of each face in this image
# face_locations = face_recognition.face_locations(image)
#
# for face_location in face_locations[:1]:
#     # Face coordinates
#     global top, right, bottom, left
#     top, right, bottom, left = face_location
#
#     # Resize image and save it
#     face_image = image[top:bottom, left:right]
#     pil_image = Image.fromarray(face_image)
#     # pil_image.thumbnail((300, 450))
#     pil_image.show()

# profile_face_photos_names = ['127229.jpg', '678783.jpg', '735308.jpg', '1372137.jpg', '1808766.jpg']
landmarks_list = []
face_photos_filenames = []
for i in range(500):
    fr_image = face_recognition.load_image_file(img_dir + photo_names_list[i])
    face_landmarks = face_recognition.face_landmarks(fr_image, model = 'small')
    if len(face_landmarks):
        landmarks_list.append(face_landmarks)
        face_photos_filenames.append(photo_names_list[i])

distance_list = [euc_distance(landmark) for landmark in landmarks_list]
profile_idxs = [idx[0] for idx in np.argwhere(np.logical_or(np.less(distance_list, 0.9), np.greater(distance_list, 1.1)))]
for idx in profile_idxs:
    os.rename(img_dir + photo_names_list[idx], img_dir + 'profile_photos/' + photo_names_list[idx])

# distance_sort_idx = np.argsort(distance_list)
# distance_sorted = np.array(distance_list)[distance_sort_idx]
# photos_sorted = [corresponding_photos[i] for i in distance_sort_idx]

# distance < 0.9 or distance > 1.1