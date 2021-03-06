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

from datamanager import DataManager

from scipy.misc import imsave

from image3d import Image3D


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

    hough_radii = np.arange(200, 250, 3)
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

def load_and_threshold(isq_filename, output_path):

    raw_stack = read_isq_file(isq_filename)

    threshold = threshold_otsu(raw_stack)

    thresholded = (raw_stack > threshold).view(Image3D)

    thresholded.save(output_path)

    return thresholded

def strip_outside_circle(input_array, center, radius):
    """Return array generated by setting all values in input_array outside 
    circle of given center and radius to zero."""

    cx, cy = center
    r = radius
    xdim, ydim = input_array.shape

    y, x = np.ogrid[-cx:xdim-cx,-cy:ydim-cy]
    # Small adjustment for aliasing
    r = r - 2
    mask = x*x + y*y >= r*r

    output_array = np.copy(input_array)
    output_array[mask] = 0

    return output_array

def threshold_and_strip(isq_filename):

    pm = PathManager(isq_filename)

    thresholded = load_stack_from_path(pm.spath('thresholded'))

    stripped_stack = strip_stack(thresholded).view(Image3D)

    stripped_stack.save(pm.spath('stripped'))
                                       
    #save_stack('stripped', stripped_stack)

def dthreshold_and_strip(isq_filename):

    dm = DataManager(isq_filename)

    thresholded = load_stack_from_path(pm.spath('thresholded'))

    stripped_stack = strip_stack(thresholded).view(Image3D)

    stripped_stack.save(pm.spath('stripped'))
                                       
    #save_stack('stripped', stripped_stack)

def strip_stack(thresholded):
    """Generate stack found by stripping the outer solid annulus from each image.

    To do, this we take a number of planar samples along the z direction from the 
    stack, then find the center and radius of the inner edge of the annulus using
    Hough transforms. We then generate a stack by setting everything outside this
    region to zero for each image in the stack, using linear interpolation to 
    determine the center and radius of the inner edge at each point. This is much
    faster than explicitly taking the Hough transform for each image in the stack.
    """

    n_samples = 5

    xdim, ydim, zdim = thresholded.shape

    z_samples = map(int, np.linspace(0, zdim-1, n_samples))

    circle_samples = [find_inner_circle_parameters(thresholded[:,:,z])
                       for z in z_samples]

    xs, ys, rs = zip(*circle_samples)

    stripped_planes = []
    for z in range(zdim):

        x = np.interp(z, z_samples, xs)
        y = np.interp(z, z_samples, ys)
        r = np.interp(z, z_samples, rs)

        stripped = strip_outside_circle(thresholded[:,:,z], (x, y), r)

        stripped_planes.append(stripped)


    stripped_stack = np.dstack(stripped_planes)

    return stripped_stack

def dm_threshold_and_strip(isq_filename):

    dm = DataManager(isq_filename)

    raw_stack_path = dm.spath('raw_stack')

    raw_stack = Image3D.from_path(raw_stack_path)

    threshold = threshold_otsu(raw_stack)

    thresholded = (raw_stack > threshold).view(Image3D)

    stripped_stack = strip_stack(thresholded).view(Image3D)

    stripped_stack.save(dm.spath('stripped'))

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('isq_filename', help="Path to file with CT data.")
    
    args = parser.parse_args()

    dm_threshold_and_strip(args.isq_filename)

    #threshold_and_strip(args.isq_filename)

    #pm = PathManager(args.isq_filename)
    #load_and_threshold(args.isq_filename, pm.spath('thresholded'))
    #threshold_and_strip(args.isq_filename)

if __name__ == "__main__":
    main()

