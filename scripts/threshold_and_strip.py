"""Load CT data, threshold and strip outer tube."""

import argparse

import numpy as np

from skimage.filters import threshold_otsu
from skimage.transform import hough_circle

from read_isq import read_isq_file

from jicbioimage.transform import (
    find_edges_sobel
)

from stacktools import save_stack, load_stack_from_path

def find_n_best_hough_circles(radii, hough_res, n):
    """Given the radii and hough accumulators for those radii, find the n
    accumulators with the best circles, returning the centers and radii of
    each of those circles in the form (x1, y1, r1), (x2, y2, r2), ...."""

    n_radii = len(radii)

    max_by_radii = [(np.max(hough_res[r,:,:]), r) for r in range(n_radii)]
    max_by_radii.sort(reverse=True)

    best_scores = max_by_radii[:2]

    def flatten_where_result(where_result):
        return [e[0] for e in where_result]

    circles = []
    for score, index in best_scores:
        x, y = flatten_where_result(np.where(hough_res[index,:,:]==score))
        r = radii[index]
        circles.append((x, y, r))

    return circles

def find_inner_circle_parameters(plane_array):
    """Given a single planar image (e.g. a section from CT data), find the
    locations of the inner of two circles in the image."""

    xdim, ydim = plane_array.shape

    edges = find_edges_sobel(plane_array)

    hough_radii = np.arange(200, 250, 1)
    hough_res = hough_circle(edges, hough_radii)

    # Find the two clearest circles
    c1, c2 = find_n_best_hough_circles(hough_radii, hough_res, 2)

    # Work out which is the inner circle
    r1 = c1[2]
    r2 = c2[2]
    if r1 > r2:
        inner_circle_radius = r2
        cx, cy, r = c2
    else:
        inner_circle_radius = r1
        cx, cy, r = c1

    return cx, cy, r

def load_and_threshold(isq_filename):

    raw_stack = read_isq_file(isq_filename)

    threshold = threshold_otsu(raw_stack)

    thresholded = raw_stack > threshold

    save_stack('thresholded', thresholded)

def threshold_and_strip(isq_filename):

    thresholded = load_stack_from_path('output/thresholded.stack')

    z_samples = [0, 1000, 2000]

    for z in z_samples:
        print find_inner_circle_parameters(thresholded[:,:,z])

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('isq_filename', help="Path to file with CT data.")
    
    args = parser.parse_args()

    threshold_and_strip(args.isq_filename)

if __name__ == "__main__":
    main()

