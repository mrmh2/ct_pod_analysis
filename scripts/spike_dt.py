import os
import errno
import argparse

from skimage.filters import (
    threshold_otsu
)

from scipy.ndimage.morphology import (
    binary_erosion, 
    binary_dilation,
    distance_transform_cdt,
)

from jicbioimage.core.image import Image

from pathmanager import PathManager

from scipy.misc import imsave

def mkdir_p(path):
    try:
        os.makedirs(path)   
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def dt_and_threshold(input_plane, threshold=75):
    t_otsu = threshold_otsu(input_plane)
    thresholded = input_plane > t_otsu
    dt = distance_transform_cdt(thresholded)

    return dt > threshold

def spike_dt(data_file):

    pm = PathManager(data_file, working_base='/localscratch/ct_analysis')
    stack_path = pm.spath('raw_stack.stack')

    z = 273
    filename = "z{}.png".format(z)
    full_path = os.path.join(stack_path, filename)

    plane = Image.from_file(full_path)

    threshold = threshold_otsu(plane)
    thresholded = plane > threshold
    imsave('t.png', thresholded)
    dt = distance_transform_cdt(thresholded)
    imsave('dt.png', dt)
    print dt.max()
    tdt = dt > 70

    imsave('tdt.png', tdt)

def sop(data_file):
    pm = PathManager(data_file, working_base='/localscratch/ct_analysis')

    stack_path = pm.spath('raw_stack.stack')
    output_stack_path = pm.spath('dt_stack')

    mkdir_p(output_stack_path)

    zdim = len(os.listdir(stack_path))

    for z in range(zdim):
        filename = "z{}.png".format(z)
        full_path = os.path.join(stack_path, filename)
        plane = Image.from_file(full_path)

        transformed = dt_and_threshold(plane)


        full_output_path = os.path.join(output_stack_path, filename)
        imsave(full_output_path, transformed)
    

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('data_file', help="Path to data file")

    args = parser.parse_args()

    sop(args.data_file)

if __name__ == "__main__":
    main()
