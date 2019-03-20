import face_recognition
import os
from PIL import Image


# Image proportions
#x_over_y = 2/3
x_over_y = 1/1

x_radius_mult_factor = 1.5
y_radius_top_mult_factor = 2.5
y_radius_bot_mult_factor = 2


def get_coordinates_for_full_head(image_width, image_length, midpoint_x, midpoint_y, radius_x, radius_y):
    """ Zoom out from face coordinates to show the full head of the person in the picture """
    global top, right, bottom, left

    # Check to what side the midpoints are closest
    midpoint_below_center = image_length - midpoint_y < midpoint_y
    midpoint_right_from_center = image_width - midpoint_x < midpoint_x

    # Correct coordinates to show full head instead of only face
    if midpoint_below_center:
        bottom = round(midpoint_y + y_radius_bot_mult_factor * radius_y)
        if bottom > image_length:
            bottom = image_length
            top = round(midpoint_y - (bottom - midpoint_y))
        else:
            top = round(midpoint_y - y_radius_top_mult_factor * radius_y)
    else:
        top = round(midpoint_y - y_radius_top_mult_factor * radius_y)
        if top < 0:
            bottom = round(midpoint_y * (1 + y_radius_bot_mult_factor / y_radius_top_mult_factor))
            top = 0
        else:
            bottom = bottom = round(midpoint_y + y_radius_bot_mult_factor * radius_y)
    if midpoint_right_from_center:
        right = round(midpoint_x + x_radius_mult_factor * radius_x)
        if right > image_width:
            right = image_width
            left = round(midpoint_x - (right - midpoint_x))
        else:
            left = round(midpoint_x - x_radius_mult_factor * radius_x)
    else:
        left = round(midpoint_x - x_radius_mult_factor * radius_x)
        if left < 0:
            left = 0
            right = round(2 * midpoint_x)
        else:
            right = round(midpoint_x + x_radius_mult_factor * radius_x)


def resize_to_ratio(image_width, image_length):
    """ Resize the image to the ratio in 'x_over_y' """
    global top, right, bottom, left
    
    # Enlarge dimension (x or y) that is smaller than it is supposed to be, if possible
    if right - left < (bottom - top) * x_over_y:
        diff = (bottom - top) * x_over_y - (right - left)
        right = min(right + round(diff / 2), image_width)
        left = max(left - round(diff / 2), 0)
    else:
        diff = (right - left) - (bottom - top) * x_over_y
        bottom = min(bottom + round(diff / 2), image_length)
        top = max(top - round(diff / 2), 0)


def main(image_dir, output_dir):

    image = face_recognition.load_image_file(image_dir)
    image_length, image_width = image.shape[:2]

    # Find the location of each face in this image
    face_locations = face_recognition.face_locations(image)

    for face_location in face_locations[:1]:

        # Face coordinates
        global top, right, bottom, left
        top, right, bottom, left = face_location
        midpoint_x = (right + left)/2
        midpoint_y = (top + bottom)/2
        radius_x = right - midpoint_x
        radius_y = bottom - midpoint_y

        # Standardize image
        get_coordinates_for_full_head(image_width, image_length, midpoint_x, midpoint_y, radius_x, radius_y)
        resize_to_ratio(image_width, image_length)

        # Resize image and save it
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        # pil_image.show()
        pil_image.save(output_dir + image_filename)

# ------------------------------------------------------------------------------------------------------------------------


# ugly
images_dir = './storage_mount/images_end_ugly/'
output_dir = './storage_mount/images_end_ugly_cropped/'
images_list = os.listdir(images_dir)
images_list = [image for image in images_list if not image.startswith('.DS')]

# Run script (I'm not familiar with the 'if name == main' stuff yet)
for image_filename in images_list:
    image_dir = images_dir + image_filename
    main(image_dir, output_dir)


# pretty
images_dir = './storage_mount/images_end_pretty/'
output_dir = './storage_mount/images_end_pretty_cropped/'
images_list = os.listdir(images_dir)
images_list = [image for image in images_list if not image.startswith('.DS')]

# Run script (I'm not familiar with the 'if name == main' stuff yet)
for image_filename in images_list:
    image_dir = images_dir + image_filename
    main(image_dir, output_dir)