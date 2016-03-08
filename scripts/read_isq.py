"""Read ISQ file."""

import os
import io
import argparse

import numpy as np

import scipy.misc

from skimage.filters import sobel

# 44 bytes
# 24 bytes stuff
# 440 bytes
# 3 bytes stuff


def bytes_to_int(bytes):

    value = 0

    for n, b in enumerate(bytes):
        value += ord(b) << (n * 8)

    return value

def dump_bytes(bytes):

    for n, b in enumerate(bytes):
        print n, ord(b)

def read_isq_file(filename):
    """Read an ISQ file."""

    with io.open(filename, 'rb') as f:
        header_bytes = f.read(2048)

        xdim = bytes_to_int(header_bytes[44:47])
        ydim = bytes_to_int(header_bytes[48:51])
        zdim = bytes_to_int(header_bytes[52:55])

        tmp_int = bytes_to_int(header_bytes[56:60])

        #more_bytes = f.read(xdim * ydim * 2 * zdim)
        #more_bytes = f.read(xdim * ydim * 2 * 600)
        more_bytes = f.read()

        im_array = np.fromstring(more_bytes, dtype='<i2')

    nim = np.reshape(im_array, (xdim, ydim, -1), order='F')
 

    return nim

def imsave_signed(filename, array):

    array = np.maximum(array, 0)
    scipy.misc.imsave(filename, array)

def spike_ct(filename):

    image = read_isq_file(filename)

    #90 - 170

    # 279 - 575 for large

    path = 'stacklet'

    for z in range(279, 575):
        filename = os.path.join(path, 'sample_Z{}.png'.format(str(z)))
        imsave_signed(filename, image[:,:,z])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    args = parser.parse_args()

    spike_ct(args.filename)

if __name__ == '__main__':
    main()
