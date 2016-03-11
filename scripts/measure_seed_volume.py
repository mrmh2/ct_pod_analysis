"""Measure volume of a single seed."""

import argparse

import numpy as np

from skimage.filters import (
    threshold_otsu
)

from image3d import Image3D

def measure_seed_volume(seed_stack):

    print seed_stack.shape

    threshold = threshold_otsu(seed_stack)
    thresholded = seed_stack > threshold

    print np.sum(thresholded)

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('seed_stack', help='Path to seed stack')

    args = parser.parse_args()

    seed_stack = Image3D.from_path(args.seed_stack)

    measure_seed_volume(seed_stack)

if __name__ == "__main__":
    main()
