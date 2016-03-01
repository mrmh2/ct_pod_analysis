"""Given an ISQ file and a YAML file containing seed centroids, generate stacks
for each seed in the file."""

import argparse

import yaml

from extract_single_seed_stack import find_section_of_isq_file
from stacktools import save_stack

def generate_seed_stacks(isq_filename, seed_filename):

    with open(seed_filename) as f:
        seed_centroids = yaml.load(f)

    for name, centroid in seed_centroids.items():
        print centroid

        try:
            stack = find_section_of_isq_file(isq_filename, centroid, 50)
        except IndexError:
            continue

        save_stack(name, stack)

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('isq_filename', 
                        help='Path to file with CT data')
    parser.add_argument('seed_filename', 
                        help='Path to file with seed centroids')

    args = parser.parse_args()

    generate_seed_stacks(args.isq_filename, args.seed_filename)


if __name__ == "__main__":
    main()
