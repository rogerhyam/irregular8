
import os
from PIL import Image, ImageStat, ImageChops

directory = "images"


def process_image(file_path):

    width_offset = 0.1  # percentage of the width of image
    height_offset = 0.1
    window_size = 100  # size of the sampling box (pixels each side)

    # Open image using Image module
    img = Image.open(file_path)
    # Show actual Image
    # im.show()

    width, height = img.size

    # cropped_img.show()

    # loop down the image
    perf_start_y = 100
    for y in range(height):

        # window
        top_left_x = width_offset * width
        top_left_y = y
        bottom_right_x = top_left_x + window_size
        bottom_right_y = top_left_y + window_size
        window = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)

        # get that window
        cropped_img = img.crop(window).convert('L')
        stat = ImageStat.Stat(cropped_img)
        avg = stat.mean[0]

        if avg == 255:
            if y > perf_start_y:
                shift_y = (y - perf_start_y)
            else:
                shift_y = perf_start_y - y
            break

    img = ImageChops.offset(img, 0, shift_y * -1)
    img.save("3_" + file_path)
    # img.show()


for filename in os.listdir(directory):
    if filename == ".DS_Store":
        continue
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        process_image(f)
