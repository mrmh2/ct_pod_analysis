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

from jicbioimage.illustrate import AnnotatedImage

import SimpleITK as sitk

from extract_single_seed_stack import find_section_of_isq_file

def find_seeds_in_isq_image(filename):

    isq_stack = read_isq_file(filename)

    tval = threshold_otsu(isq_stack)

    thresh = isq_stack > tval

    save_stack('th', thresh)

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
    
def strip_outside_inner_circle(plane_array):
    """Given a single planar image (e.g. a section from CT data), find the
    locations of the inner and outermost strong circles in the image and
    remove everything outside the inner one."""

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

    # Sanity check
    expected_r = 204
    tol = 2
    r_in_bound = expected_r-tol < inner_circle_radius < expected_r+tol
    if not r_in_bound:
        print "Inner circle radius: {}".format(inner_circle_radius)
        raise Exception("Circle detection probably failed")

    y, x = np.ogrid[-cx:xdim-cx,-cy:ydim-cy]
    # Small adjustment for aliasing
    r = r - 2
    mask = x*x + y*y >= r*r

    output_array = np.copy(plane_array)
    output_array[mask] = 0

    return output_array

def spike_circles():

    stack = load_stack_from_path('output/th.stack')
    
    # stripped_planes = [strip_outside_inner_circle(stack[:,:,z]) for z in
    #                    range(5)]

    # stripped_stack = np.dstack(stripped_planes)

    # save_stack('stripped', stripped_stack)

    for z in range(10, 600):
        filename = "spikey/z{}.png".format(z)
        stripped_plane = strip_outside_inner_circle(stack[:,:,z])
        imsave(filename, stripped_plane)
        print filename
    

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

def spike_distance_transform():
    stack = load_stack_from_path('spikey/')

    print stack.shape

    dt = distance_transform_cdt(stack)

    print np.max(dt)

    tdt = dt > 10

    save_stack('tdt', tdt)

    ccs = label(tdt)
    print np.unique(ccs)

    wseed5 = np.where(ccs==5)

    float_center = map(np.mean, wseed5)
    int_center = map(int, float_center)


    # save_stack('nccs', ccs)

    # itk_image = sitk.GetImageFromArray(mdt)
    # ccs_filter = sitk.ConnectedComponentImageFilter()
    # ccs_image = ccs_filter.Execute(itk_image)
    # array = sitk.GetArrayFromImage(ccs_image)
    # print np.unique(array)
    # save_stack('array', array)

def find_seed_centroids(isq_filename):
    """Load given ISQ filename and find the coordinates of all of the seeds
    in that ISQ file."""

    stack = load_stack_from_path('output/stripped.stack')

    distances = distance_transform_cdt(stack)
    seeds = distances > 10
    seed_label_array = label(seeds)

    seed_labels = {}
    for seed_label in np.unique(seed_label_array):
        float_center = map(np.mean, np.where(seed_label_array==seed_label))
        int_center = map(int, float_center)

        seed_name = 'seed{}'.format(seed_label)

        seed_labels[seed_name] = tuple(int_center)

    with open('seeds.yml', 'w') as f:
        yaml.dump(seed_labels, f)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='Path to ISQ file')

    args = parser.parse_args()

    find_seed_centroids(args.filename)

if __name__ == "__main__":
    main()
