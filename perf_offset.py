

from PIL import Image

test_file_path = "images/2022-08-26_012.jpg"
width_offset = 0.1  # percentage of the width of image
window_size = 100  # size of the sampling box (pixels each side)


# Open image using Image module
img = Image.open(test_file_path)
# Show actual Image
# im.show()

width, height = img.size

top_left_x = width_offset * width
top_left_y = 0

bottom_right_x = top_left_x + window_size
bottom_right_y = top_left_y + window_size

window = (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
cropped_img = img.crop(window).convert('L')
stat = ImageStat.Stat(cropped_img)

print('banana')
print(stat.mean[0])

# cropped_img.show()

# loop down the image
# for i in range(height):
#    print(height * i)
