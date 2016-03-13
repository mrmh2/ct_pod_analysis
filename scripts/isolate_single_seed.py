"""Isolate a single seed from a stack containing that seed."""

import argparse

import numpy as np

from image3d import Image3D

from scipy.ndimage import (
    gaussian_filter,
    sobel,
    binary_dilation
)

from skimage.filters import (
    threshold_otsu
)

from skimage.morphology import watershed

def sobel_magnitude_nd(z_stack):
    """Find edges."""

    n_dim = len(z_stack.shape)

    directional_filters = [np.zeros(z_stack.shape) for _ in range(n_dim)]

    [sobel(z_stack, axis, directional_filters[axis])
     for axis, single_filter 
     in enumerate(directional_filters)]

    magnitude = np.sqrt(sum(single_axis ** 2 
                            for single_axis 
                            in directional_filters))

    return magnitude

def save_wrapper(image3d, name):
    
    return

def isolate_single_seed(stack_path, output_path):
    """Load stack then isolate seed."""

    sigma = 10
    iterations = 1

    raw_stack = Image3D.from_path(stack_path)

    print raw_stack.shape

    smoothed = gaussian_filter(raw_stack, sigma).view(Image3D)

    edges = sobel_magnitude_nd(smoothed).view(Image3D)

    #edges.save('edges')

    labels = np.zeros(raw_stack.shape)
    cx, cy, cz = map(lambda x: x/2, raw_stack.shape)
    labels[cx, cy, cz] = 1

    threshold = threshold_otsu(smoothed)
    thresholded = smoothed > threshold

    #thresholded.view(Image3D).save('thresh')

    segmentation = watershed(edges, markers=labels, mask=thresholded)

    #segmentation.view(Image3D).save('seg')

    dilated = binary_dilation(segmentation, iterations=iterations)

    isolate = np.multiply(raw_stack, dilated)

    isolate.view(Image3D).save(output_path)

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('stack_path', help='Path to stack')
    parser.add_argument('output_path', help='Output path')

    args = parser.parse_args()

    isolate_single_seed(args.stack_path, args.output_path)

if __name__ == "__main__":
    main()
