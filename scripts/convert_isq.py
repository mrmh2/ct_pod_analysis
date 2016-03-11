"""Convert ISQ file into stack, handling large ISQ files gracefully."""

import argparse

import read_isq

def convert_large_isq_file(isq_filename, stack_path):

    pass


def main():

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('isq_filename', help="Path to ISQ file")
    parser.add_argument('stack_path', help="Path to write output stack")

    args = parse.parse_args()

    convert_large_isq_file(args.isq_filename, args.stack_path)


if __name__ == "__main__":
    main()


