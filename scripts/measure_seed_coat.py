"""Measure brassica seed coat thickness."""

import argparse

import math

import numpy as np

from scipy.misc import imsave

from skimage.filters import threshold_otsu
from skimage.measure import profile_line
from skimage.draw import line

from jicbioimage.illustrate import AnnotatedImage

from stacktools import load_stack_from_path, save_stack

class Seed(object):
    pass

def find_center(seed_stack):

    threshold = threshold_otsu(seed_stack)

    thresholded = seed_stack > threshold
    
    float_center = map(np.mean, np.where(thresholded != 0))

    return map(int, float_center)

def analyse_line_profile(line_profile):
    """Line profile starts from center and past edge to dark region."""

    peak_max = np.max(line_profile)

    #print 'max', peak_max

    first_max_index = np.where(line_profile == peak_max)[0][0]

    median = np.median(line_profile[:first_max_index])

    segment = line_profile[first_max_index-5:first_max_index+5]

    # print segment
    # print segment > median

    # Walk forwards to find end of peak
    end_pos = first_max_index
    while line_profile[end_pos] > median:
        end_pos += 1

    # Walk backwards to find start of peak
    start_pos = first_max_index
    while line_profile[start_pos] > median:
        start_pos -= 1

    return end_pos - start_pos

def measure_line_profile(image, line_start, line_end):
    
    pline = profile_line(image, line_start, line_end)
    return analyse_line_profile(pline)

def record_line_profile(image, line_start, line_end, filename):

    pline = profile_line(image, line_start, line_end)

    print analyse_line_profile(pline)

    enumerated = list(enumerate(pline))

    #print np.median(pline[100:-100])

    with open(filename, 'w') as f:
        f.write('position,intensity\n')
        values_string = '\n'.join('{},{}'.format(*v) for v in enumerated)
        f.write(values_string)

def find_line_through_point(center, theta, length):
    """Find the coordinates of the start and end of a line passing through the 
    point center, at an angle theta to the x coordinate, extending a distance
    length from the center."""

    r = length
    cx, cy = center

    xo = int(r * math.sin(theta))
    yo = int(r * math.cos(theta))

    line_start = cx, cy
    line_end = cx + xo, cy + yo

    return line_start, line_end

def draw_line_on_canvas(canvas, line_start, line_end, color=(0, 255, 0)):
    """Draw a line on the supplied canvas, from line_start to line_end."""

    line_coords = line_start + line_end
    rr, cc = line(*line_coords)
    canvas[rr, cc] = color

def measure_seed_coat_thickness(seed_stack_name):
    """Open stack and measure seed coat."""

    stack = load_stack_from_path(seed_stack_name)

    cx, cy, cz = find_center(stack)

    center_plane = stack[:,:,cz]

    plane_x = stack[cx,:,:]
    plane_y = stack[:,cy,:]
    plane_z = stack[:,:,cz]

    imsave('plane_x.png', plane_x)
    imsave('plane_y.png', plane_y)
    imsave('plane_z.png', plane_z)
    # line_start = 200, 0
    # line_end = 200, 499

    # line_start = 0, 326
    # line_end = 499, 326

    r = 150
    theta = 1.5


    #record_line_profile(center_plane, line_start, line_end, 'dump2.txt')
    canvas = AnnotatedImage.from_grayscale(center_plane)
    canvas.draw_cross(cy, cx)
    #draw_line_on_canvas(canvas, line_start, line_end)

    for theta in np.linspace(0, 2 * math.pi, 50):
        line_start, line_end = find_line_through_point((cx, cy), theta, r)
        width = measure_line_profile(center_plane, line_start, line_end)
        x, y = line_end
        canvas.text_at(str(width), y, x)

    # for theta in np.linspace(0, math.pi, 10):
    #     line_start, line_end = find_line_through_point((cx, cy), theta, r)
    #     draw_line_on_canvas(canvas, line_start, line_end)

    imsave('annotated.png', canvas)

def coat_off(seed_stack_filename):
    
    seed_stack = load_stack_from_path(seed_stack_filename)

    coat_mask = seed_stack > 160

    seed_stack[np.where(coat_mask == True)] = 0

    save_stack('coat_off', seed_stack)
    #seed_stack[coat_mask] = 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')

    seed_stack = 'data/seeds/single_seed.stack'

    #measure_seed_coat_thickness(seed_stack)
    coat_off(seed_stack)

if __name__ == "__main__":
    main() 
