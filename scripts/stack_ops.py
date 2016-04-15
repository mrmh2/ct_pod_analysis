IMAGE_EXTS = ['.png', '.tif', '.tiff']

import os
import re
import errno

from jicbioimage.core.image import Image

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

def yield_stack_from_path(input_stack_path):
    """Yield individual images from stack path."""

    all_files = os.listdir(input_stack_path)
    image_files = filter(is_image_filename, all_files)
    sorted_image_files = sorted_nicely(image_files)
    full_image_paths = [os.path.join(input_stack_path, fn) 
                        for fn in sorted_image_files]

    images = (Image.from_file(f) for f in full_image_paths)

    return images

def apply_stack_transform(input_path, output_path, transform):

    mkdir_p(output_path)

    for n, im in enumerate(yield_stack_from_path(input_path)):
        transformed = transform(im)
        fn = "z{}.png".format(n)
        with open(os.path.join(output_path, fn), 'wb') as f:
            f.write(transformed.view(Image).png())