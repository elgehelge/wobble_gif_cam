import numpy


def auto_align(rgb_imgs):
    """
    Aligns a sequence of images by shifting each image to match the previous
    """
    imgs_gray = [img.mean(axis=-1).astype(int) for img in rgb_imgs]
    relative_shift = [(0, 0)] + \
                     [min_diff_search(imgs_gray[i], imgs_gray[i + 1]) for i
                      in range(len(imgs_gray) - 1)]
    shifts = numpy.array(relative_shift).cumsum(axis=0) * -1
    right_bottom = shifts - shifts.min(axis=0)
    left_top = (shifts - shifts.max(axis=0)) * -1
    crop_l_t_r_b = numpy.concatenate([left_top, right_bottom], axis=1)
    imgs_cropped = [crop(img, *crop_size)
                    for img, crop_size in zip(rgb_imgs, crop_l_t_r_b)]
    return imgs_cropped


def min_diff_search(shift_img, base_img):
    """
    Align images by searching for minimum pixel difference in overlap

    The search is naive and does not guarantee to find the global optimum:
    - Try shifting one of the images a few pixels in any direction and measure
    - When it is not possible to do find a better shift

    Returns the locally optimal x and y distance to shift images
    """
    x, y = 0, 0
    search_options = [
        (-20, 0), (0, -20), (20, 0), (0, 20),
        (-5, 0), (0, -5), (5, 0), (0, 5),
        (-1, 0), (0, -1), (1, 0), (0, 1),
    ]
    current_diff = mean_pixel_diff(*shift(shift_img, base_img, x, y))
    found_minimum = False
    while not found_minimum:
        for count, (dx, dy) in enumerate(search_options):
            shifted_imgs = shift(shift_img, base_img, x + dx, y + dy)
            new_diff = mean_pixel_diff(*shifted_imgs)
            if new_diff < current_diff:
                x += dx
                y += dy
                current_diff = new_diff
                break  # break the for-loop and start over
            if count == len(search_options) - 1:
                found_minimum = True
    return x, y


def mean_pixel_diff(img1, img2):
    return abs(img1 - img2).mean()


def crop(img, left, top, right, bottom):
    height = img.shape[0]
    width = img.shape[1]
    return img[top:height-bottom, left:width-right]


def shift(img1, img2, x, y):
    left, right = (abs(x), 0) if x < 0 else (0, x)
    top, bottom = (abs(y), 0) if y < 0 else (0, y)
    img1_shifted = crop(img1, left, top, right, bottom)
    img2_shifted = crop(img2, right, bottom, left,  top)
    return img1_shifted, img2_shifted
