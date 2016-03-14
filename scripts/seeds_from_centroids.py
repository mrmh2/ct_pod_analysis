"""Given an ISQ file and a YAML file containing seed centroids, generate stacks
for each seed in the file."""

import os
import argparse

import yaml

from extract_single_seed_stack import find_section_of_isq_file

from datamanager import DataManager
from image3d import Image3D

def generate_seed_stacks(dm):

    seed_filename = dm.spath('seeds.yml')
    isq_filename = dm.rawpath

    with open(seed_filename) as f:
        seed_centroids = yaml.load(f)['seeds']

    for name, centroid in seed_centroids.items():
        print centroid

        try:
            stack = find_section_of_isq_file(isq_filename, centroid, 50)
        except IndexError:
            continue

        subname = os.path.join('seeds', name)
        seed_filename = dm.spath(subname)
        stack.view(Image3D).save(seed_filename)

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('isq_filename', 
                        help='Path to file with CT data')

    args = parser.parse_args()

    dm = DataManager(args.isq_filename)

    generate_seed_stacks(dm)


if __name__ == "__main__":
    main()
