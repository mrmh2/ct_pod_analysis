"""Find seeds in an ISQ image."""

import argparse

import numpy as np

import yaml

from skimage.draw import circle_perimeter
from skimage.filters import threshold_otsu
from skimage.transform import hough_circle
from skimage.measure import label

from read_isq import read_isq_file
from stacktools import save_stack, load_stack_from_path

from scipy.ndimage.morphology import (
    binary_erosion, 
    binary_dilation,
    distance_transform_cdt,

)

from scipy.misc import imread, imsave

from jicbioimage.transform import (
    find_edges_sobel
)

from extract_single_seed_stack import find_section_of_isq_file

from image3d import Image3D
from datamanager import DataManager

def find_seed_centroids(stack):
    """Find seeds in given binary stack, returning dictionary containing seed
    centroids."""

    distances = distance_transform_cdt(stack)
    seeds = distances > 10
    seed_label_array = label(seeds)

    seed_labels = {}
    for seed_label in np.unique(seed_label_array):
        float_center = map(np.mean, np.where(seed_label_array==seed_label))
        int_center = map(int, float_center)

        seed_name = 'seed{}'.format(seed_label)

        seed_labels[seed_name] = int_center

    return seed_labels

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Path to ISQ file')

    args = parser.parse_args()

    dm = DataManager(args.filename)

    stack = Image3D.from_path(dm.spath('stripped'))
    seed_labels = find_seed_centroids(stack)

    stage = {}
    stage['name'] = dm.name
    stage['seeds'] = seed_labels
    with open(dm.spath('seeds.yml'), 'w') as f:
        yaml.dump(stage, f)


if __name__ == "__main__":
    main()
