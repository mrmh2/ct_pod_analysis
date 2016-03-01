import io

import numpy as np

from skimage.filters import threshold_otsu

#import skimage.measure

from scipy.ndimage.morphology import (
    binary_erosion, 
    binary_closing,
    binary_dilation,
)

from scipy.ndimage.filters import median_filter
from scipy.ndimage.measurements import label

from stacktools import save_stack, load_stack_from_path

def bytes_to_int(bytes):

    value = 0

    for n, b in enumerate(bytes):
        value += ord(b) << (n * 8)

    return value

def fix_signed_stack(input_stack):
    """Deal with the problem of stacks with a signed integer value that probably
    shouldn't have them."""

    return np.maximum(input_stack, 0)
    
def calculate_box_bounds(center, radius):
    """Given a center position in 3D space and a radius, return the bounds of
    the box containing a sphere centered at that point with the given 
    radius."""

    xc, yc, zc = center

    z1 = zc - radius
    z2 = zc + radius
    x1 = xc - radius
    x2 = xc + radius
    y1 = yc - radius
    y2 = yc + radius

    return x1, x2, y1, y2, z1, z2

def find_section_of_isq_file(isq_filename, center, radius):
    """Return section from isq_filename as numpy array, centered at the given
    location and with the given radius."""

    x1, x2, y1, y2, z1, z2 = calculate_box_bounds(center, radius)

    ct_array = read_isq_z_range(isq_filename, z1, z2)

    smaller = ct_array[x1:x2,y1:y2,:]

    fixed_stack = fix_signed_stack(smaller)

    return fixed_stack

def extract_single_seed_stack(isq_filename, center, radius):
    """Return stack representing a single seed from the ISQ file isq_filename,
    centered at center with the given radius."""

    # xian_section = find_section_of_isq_file(isq_filename, center, radius)
    # save_stack('xian_section', xian_section)

    xian_section = load_stack_from_path('output/xian_section.stack')

    tval = threshold_otsu(xian_section)
    thresholded_stack = xian_section > tval
    #save_stack('xian_thresh', thresholded_stack)

    median_stack = median_filter(thresholded_stack, size=5)
    save_stack('xian_median', median_stack)

    selem = np.ones((5, 5, 5))
    eroded = binary_erosion(median_stack, structure=selem, iterations=3)
    save_stack('xian_eroded', eroded)

    # ccs = skimage.measure.label(eroded)
    # save_stack('xian_ccs', ccs)

    #eroded = load_stack_from_path('output/xian_eroded.stack')
    label_array = np.zeros((400, 400, 400), dtype=np.uint32)
    label(eroded, output=label_array)
    save_stack('xian_ccs', label_array)
    # labels = np.unique(ccs)

    # print labels

def read_isq_z_range(filename, zstart, zend):
    """Read slices from the ISQ file, starting at zstart and finishing at
    zend."""

    header = read_isq_header(filename)
    xdim, ydim, zdim = header['xdim'], header['ydim'], header['zdim']

    if zstart < 0:
        raise IndexError("Requested start of z stack below zero.")

    if zend > zdim:
        raise IndexError("Requested end of z stack outside range of file.")

    # 2048 byte header, then xdim * ydim 2 byte integers
    read_start = 2048 + 2 * xdim * ydim * zstart
    read_size = 2 * xdim * ydim * (zend - zstart)

    with io.open(filename, 'rb') as f:
        f.seek(read_start)
        raw_bytes = f.read(read_size)

    im_array = np.fromstring(raw_bytes, dtype='<i2')

    nim = np.reshape(im_array, (xdim, ydim, -1), order='F')

    return nim

def read_isq_header(filename):
    """Read an ISQ file header."""

    with io.open(filename, 'rb') as f:
        header_bytes = f.read(2048)

        xdim = bytes_to_int(header_bytes[44:47])
        ydim = bytes_to_int(header_bytes[48:51])
        zdim = bytes_to_int(header_bytes[52:55])

        tmp_int = bytes_to_int(header_bytes[56:60])

    labels = ('xdim', 'ydim', 'zdim')
    values = (xdim, ydim, zdim)

    return dict(zip(labels, values))

def main():
    isq_filename = "data/raw/C0000245_1.ISQ"
    center = 946, 836, 779
    #center = 806, 1146, 779
    radius = 200

    extract_single_seed_stack(isq_filename, center, radius)

if __name__ == "__main__":
    main()
