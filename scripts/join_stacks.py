"""Join two stacks with the same x and y dimensions."""

import argparse

import numpy as np

from image3d import Image3D

def join_stacks(first_stack_path, second_stack_path):

    first_stack = Image3D.from_path(first_stack_path)
    second_stack = Image3D.from_path(second_stack_path)

    first_dims = first_stack.shape
    second_dims = second_stack.shape

    if first_dims != second_dims:
        raise Exception("Stack dimensions must match")

    joined_stack = np.concatenate([first_stack, second_stack], axis=2)

    return joined_stack.view(Image3D)

def main():
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('first_stack_path', help="Path to first stack")
    parser.add_argument('second_stack_path', help="Path to second stack")

    args = parser.parse_args()

    joined_stack = join_stacks(args.first_stack_path, args.second_stack_path)

    joined_stack.save('joined')

if __name__ == "__main__":
    main()
