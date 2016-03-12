import os
import re
import errno
import argparse

import scipy.misc
import numpy as np

from PIL import Image as PILImage

from jicbioimage.core.image import Image

IMAGE_EXTS = ['.png', '.tif', '.tiff']

def mkdir_p(path):
    try:
        os.makedirs(path)   
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else: raise

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

class Image3D(np.ndarray):
    
    @classmethod
    def from_path(cls, path):
        array = load_stack_from_path(path)

        image3d = array.view(cls)

        return image3d

    def save(self, path, z_index_offset=0):
        stack_dir = path

        if not os.path.isdir(stack_dir):
            mkdir_p(stack_dir)

        xdim, ydim, zdim = self.shape

        smin, smax = np.min(self), np.max(self)
        scaled = np.uint8(255 * ((self - smin) / float(smax - smin)))

        for z in range(zdim):
            filename = 'z{}.png'.format(z+z_index_offset)
            full_name = os.path.join(stack_dir, filename)
            im = PILImage.fromarray(scaled[:,:,z])
            im.save(full_name)
            
    def tobytes(self):
        """Fixes an incompatility problem with some PIL versions."""

        return self.tostring()
