from pypexels import PyPexels
import requests
import os

api_key = '563492ad6f91700001000001b0bcd4f536714dee97e3bfc0624ab9cb'

img_dir = './storage_mount/images_intermediate_pexels/'
photo_names_list = [file for file in os.listdir(img_dir) if not file.startswith('.DS')]
photo_ids = [int(file.split('.')[0]) for file in photo_names_list]

# instantiate PyPexels object
py_pexels = PyPexels(api_key=api_key)

face_photos = py_pexels.search(query='face')
page_count = 1
while face_photos.has_next:
    for photo in face_photos.entries:
        if photo.id not in photo_ids:
            photo_url = photo.src.get('large')
            response = requests.get(photo_url)
            if response.status_code == 200:
                with open("./storage_mount/images_intermediate_pexels/" + str(photo.id) + ".jpg", 'wb') as f:
                    f.write(response.content)
        # photo_code = photo.url.split('-')[-1][:-1]
        # if photo_code not in photo_names_list:
        #     photo_url = 'https://images.pexels.com/photos/' + photo_code + '/pexels-photo-' + photo_code + '.jpeg'
        #     response = requests.get(photo_url)
        #     if response.status_code == 200:
        #         with open("./storage_mount/images_intermediate_pexels/" + photo_code + ".jpg", 'wb') as f:
        #             f.write(response.content)
    # no need to specify per_page: will take from original object
    face_photos = face_photos.get_next_page()
    page_count += 1
    print('Page number: ', page_count)

# -----------------------------------------------------------------------------------------------------------------------
