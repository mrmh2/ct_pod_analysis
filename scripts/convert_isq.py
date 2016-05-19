"""Convert ISQ file into stack, handling large ISQ files gracefully."""

import argparse

import numpy as np

from read_isq import read_isq_segment

from image3d import Image3D
from datamanager import DataManager

import scipy.misc

def convert_large_isq_file(isq_filename, stack_path):

    chunk_size = 20
    position = 0
    while True:
        print "Reading {}".format(position/chunk_size)
        try:
            part_array = read_isq_segment(isq_filename, position, chunk_size)
            #conv_array = part_array.astype(np.int32) - part_array.min()
            conv_array = np.maximum(part_array, 0)
            conv_array.view(Image3D).save(stack_path, position)
        except IOError:
            break

        position += chunk_size


def dconvert_isq_file(isq_filename):

    dm = DataManager(isq_filename)

    stack_path = dm.spath('raw_stack')

    convert_large_isq_file(isq_filename, stack_path)

def main():

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('isq_filename', help="Path to ISQ file")

    args = parser.parse_args()

    dconvert_isq_file(args.isq_filename)
    #spikey(args.isq_filename)

if __name__ == "__main__":
    main()


