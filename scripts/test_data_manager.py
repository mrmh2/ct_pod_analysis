"""Test data manager features."""

import argparse

from datamanager import DataManager

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('data_file', help="Path to data file")
    args = parser.parse_args()

    dm = DataManager(args.data_file)

    print dm.spath('some_stack')

if __name__ == '__main__':
    main()