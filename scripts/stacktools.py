"""Tools and tests for operating on 3D stacks."""

import re
import os

import numpy as np

import scipy.misc

import skimage.draw
import skimage.measure
from skimage.filters import threshold_otsu

from scipy.ndimage.morphology import (
    binary_erosion, 
    binary_dilation,
)

from skimage.morphology import (
    convex_hull_image
)

from jicbioimage.core.image import Image

IMAGE_EXTS = ['.png', '.tif', '.tiff']
HERE = os.path.dirname(__file__)
OUTPUT = os.path.join(HERE, '..', 'output')

def load_stack_from_path(input_stack_path):
    """Load a stack from a given path."""

    all_files = os.listdir(input_stack_path)
    image_files = filter(is_image_filename, all_files)
    sorted_image_files = sorted_nicely(image_files)
    full_image_paths = [os.path.join(input_stack_path, fn) 
                        for fn in sorted_image_files]

    all_images = [Image.from_file(fn) for fn in full_image_paths]

    stack = np.dstack(all_images)

    return stack

def sorted_nicely( l ):
    """ Sort the given iterable in the way that humans expect."""
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(l, key = alphanum_key)

def is_image_filename(filename):
    """Decide whether a filename is an image based on a list of allowed
    extensions."""

    base, ext = os.path.splitext(filename)

    if ext in IMAGE_EXTS:
        return True

    return False

def test_is_image_filename():

    image_filename = 'test.png'
    not_an_image = 'test.txt'

    assert( is_image_filename(image_filename) )
    assert( not is_image_filename(not_an_image) )

def section_stack(input_stack):

    x, y = 1250, 1000
    xdim, ydim = 500, 500

    return input_stack[x:x+xdim,y:y+ydim,:]

def save_stack(stack_name, stack):

    stack_dir = os.path.join(OUTPUT, stack_name + '.stack')

    if not os.path.isdir(stack_dir):
        os.mkdir(stack_dir)

    xdim, ydim, zdim = stack.shape

    for z in range(zdim):
        filename = 'z{}.png'.format(z)
        full_name = os.path.join(stack_dir, filename)
        scipy.misc.imsave(full_name, stack[:,:,z])

def imsave(filename, image):
    
    full_path = os.path.join(OUTPUT, filename)

    scipy.misc.imsave(full_path, image)
    
def spike_stack():

    input_stack_path = 'stacklet'

    all_files = os.listdir(input_stack_path)
    image_files = filter(is_image_filename, all_files)
    sorted_image_files = sorted_nicely(image_files)
    full_image_paths = [os.path.join(input_stack_path, fn) 
                        for fn in sorted_image_files]

    all_images = [Image.from_file(fn) for fn in full_image_paths]

    stack = np.dstack(all_images)

    sectioned_stack = section_stack(stack)

    save_stack('sectioned', sectioned_stack)

def extract_single_seed():
    input_stack_path = 'sectioned.stack'

    all_files = os.listdir(input_stack_path)
    image_files = filter(is_image_filename, all_files)
    sorted_image_files = sorted_nicely(image_files)
    full_image_paths = [os.path.join(input_stack_path, fn) 
                        for fn in sorted_image_files]

    all_images = [Image.from_file(fn) for fn in full_image_paths]

    stack = np.dstack(all_images)

    tval = threshold_otsu(stack)

    thresholded_stack = stack > tval

    #save_stack('thresh', thresholded_stack)

    selem = np.ones((5, 5, 5))

    eroded = binary_erosion(thresholded_stack, structure=selem)

    #save_stack('eroded', eroded)

    ccs = skimage.measure.label(eroded)

    labels = np.unique(ccs)

    #print ccs[250, 250, 100]
    seed = np.where(ccs == 148)

    mask = np.zeros(ccs.shape, dtype=np.uint8)

    mask[seed] = 255

    dilated = binary_dilation(mask, structure=selem, iterations=2)

    save_stack('dilated', dilated)

    mask_mult = dilated / np.max(dilated)

    single_seed = np.multiply(mask_mult, stack)

    save_stack('single_seed', single_seed)
    

    # _, _, zdim = dilated.shape
    # nstack = []
    # for z in range(zdim):
    #     nstack.append(convex_hull_image(dilated[:,:,z]))

    # fstack = np.dstack(*nstack)

    # save_stack('convex_hull', fstack)
    

    #print len(seed[0])

def spike_stuff():
    
    example_fn = 'sectioned.stack/z100.png'

    start_slice = Image.from_file(example_fn)

    imsave('start_slice.png', start_slice)

    line_start = 10, 10
    line_end = 490, 490

    pline = skimage.measure.profile_line(start_slice, line_start, line_end,
                                         order=0)

    print np.min(pline), np.max(pline)

    graphlet = np.zeros((200, 800), dtype=np.uint8)

    for n, h in enumerate(pline):
        graphlet[199-h, n] = 255

    imsave('graphlet.png', graphlet)

    rr, cc = skimage.draw.line(*(line_start + line_end))

    start_slice[rr, cc] = 255

    imsave('annotated_image.png', start_slice)

    enumerated = list(enumerate(pline))

    with open('dump.txt', 'w') as f:
        f.write('position,intensity\n')
        values_string = '\n'.join('{},{}'.format(*v) for v in enumerated)
        f.write(values_string)

def main():

    pass

    # single = 'stacklet/sample_Z300.png'
    # im = Image.from_file(single)

    # x, y = 1250, 1000
    # xdim, ydim = 500, 500
    # section = im[x:x+xdim,y:y+ydim]
    # imsave('section.png', section)
    
    #spike_stack()

    #spike_stuff()

    #segment_it()



if __name__ == "__main__":
    main()
