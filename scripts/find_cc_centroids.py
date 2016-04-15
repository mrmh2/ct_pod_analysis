"""Find connected component centroids and output."""

import argparse

from datamanager import DataManager

from jicbioimage.segment import connected_components

from skimage.measure import (
    label
)

from stack_ops import yield_stack_from_path

def yield_regions(segmentation):
    for i in segmentation.identifiers:
        region = segmentation.region_by_identifier(i)
        yield region

def find_component_centroids(image):

    ccs = connected_components(image, background=0)

    return [map(int, r.centroid) for r in yield_regions(ccs)]

def dcc_centroids(isq_filename):

    dm = DataManager(isq_filename, working_base='/Users/hartleym/working/ct_analysis')

    input_path = dm.spath('threshdt')

    with open('centroids.txt', 'w') as f:
        for n, image in enumerate(yield_stack_from_path(input_path)):
            centroids = find_component_centroids(image)
            for c in centroids:
                f.write("{}\n".format(c + [n]))



def main():

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('isq_filename', help="Path to ISQ file")

    args = parser.parse_args()

    dcc_centroids(args.isq_filename)

if __name__ == '__main__':
    main()