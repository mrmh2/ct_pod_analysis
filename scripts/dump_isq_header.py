"""Dump ISQ header file information."""

import io
import argparse

def bytes_to_int(bytes):

    value = 0

    for n, b in enumerate(bytes):
        value += ord(b) << (n * 8)

    return value

def dump_bytes(bytes):

    for n, b in enumerate(bytes):
        print n, ord(b)


def read_isq_header(filename):
    """Read an ISQ file header."""

    with io.open(filename, 'rb') as f:
        header_bytes = f.read(2048)

        xdim = bytes_to_int(header_bytes[44:47])
        ydim = bytes_to_int(header_bytes[48:51])
        zdim = bytes_to_int(header_bytes[52:55])

        x_scale_factor = bytes_to_int(header_bytes[56:60])
        y_scale_factor = bytes_to_int(header_bytes[60:64])
        z_scale_factor = bytes_to_int(header_bytes[64:68])
        
    dimensions = xdim, ydim, zdim

    xscale = float(x_scale_factor) / xdim
    yscale = float(y_scale_factor) / ydim
    zscale = float(z_scale_factor) / zdim

    scales = xscale, yscale, zscale

    return dimensions, scales

def dump_isq_header(isq_filename):

    dimensions, scales = read_isq_header(isq_filename)

    print("Image dimensions: {}x{}x{}".format(*dimensions))
    r1 = lambda f: round(f, 1)
    rounded = map(r1, scales)
    print("Voxel spacing (microns): {} {} {}".format(*rounded))

def main():
    
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('isq_filename', help="Path to ISQ file.")

    args = parser.parse_args()

    dump_isq_header(args.isq_filename)

if __name__ == "__main__":
    main()
