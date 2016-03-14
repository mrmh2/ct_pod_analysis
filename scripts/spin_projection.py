
import argparse

import numpy as np

from scipy.misc import imsave

from scipy.ndimage.interpolation import rotate

from image3d import Image3D

def spin_proj(stack_path):

    stack = Image3D.from_path(stack_path)


    for angle in range(200):
        output_name = 'sp/z{}.png'.format(angle)
        rotated = rotate(stack, angle)
        proj = np.amax(rotated, axis=2)
        imsave(output_name, proj)

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('stack_path', help='Path to stack')

    args = parser.parse_args()

    spin_proj(args.stack_path)



if __name__ == "__main__":
    main()