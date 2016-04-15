"""Find seed centroids from all dt centroids."""

import argparse
from collections import defaultdict

import yaml

import numpy as np

def get_point_list_from_file(filename):

    def parse_line(line):
        stripped = line.strip()
        no_brackets = stripped[1:-1]
        return [int(s) for s in no_brackets.split(',')]

    with open(filename) as f:
        all_points = np.array([parse_line(l) for l in f.readlines()])

    return all_points

def calc_distance(p1, p2):
    
    return np.linalg.norm(p1 - p2)

def dist2D(p1, p2):

    nd1 = np.array(p1)
    nd2 = np.array(p2)

    return np.linalg.norm(nd1 - nd2)

def bad_collapse(centroid_filename):

    all_points = get_point_list_from_file(centroid_filename)

    DTHRESH = 10

    # Seed the point groups
    p0 = all_points[100]
    point_groups = {tuple(p0) : [p0]}

    def closest_point_and_distance(p):
        all_distances = [(calc_distance(p, np.array(c)), c) for c in point_groups]

        all_distances.sort()

        return all_distances[0]

    point = all_points[1]
    dist, centroid = closest_point_and_distance(point)

    if dist < DTHRESH:
        pass
    else:
        point_groups[tuple(point)] = [point]

    print point_groups

def collapse_centroids(centroid_filename):

    all_points = get_point_list_from_file(centroid_filename)

    labels = {tuple(p) : n for n, p in enumerate(all_points)}

    DTHRESH = 50
    CENTER = np.array([256, 256])
    DTUBE = 150

    label_eqs = defaultdict(set)

    stage = {}
    stage['name'] = "C0000230.ISQ"

    for p0 in all_points:
        for p1 in all_points:
            if calc_distance(p0, p1) < DTHRESH:
                label_eqs[tuple(p0)].add(tuple(p1))
                #print labels[tuple(p0)], labels[tuple(p1)]

    all_centroids = set([])


    for eq_set in label_eqs.values():
        centroid_float = np.mean([np.array(i) for i in eq_set], axis=0)
        centroid_int = map(int, centroid_float)
        all_centroids.add(tuple(centroid_int))

    filtered_centroids = set([])
    for centroid in all_centroids:
        x, y, _ = centroid
        if dist2D((x, y), (CENTER)) < DTUBE:
            filtered_centroids.add(centroid)

    seed_labels = {}

    for n, centroid in enumerate(filtered_centroids):
        name = "seed{}".format(n)
        seed_labels[name] = list(centroid)

    stage['seeds'] = seed_labels

    with open('seeds.yml', 'w') as f:
        yaml.dump(stage, f)


def main():

    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('centroid_filename', help="Path to centroids file")

    args = parser.parse_args()

    collapse_centroids(args.centroid_filename)

if __name__ == '__main__':
    main()