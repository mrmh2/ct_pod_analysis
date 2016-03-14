"""Work queues."""

import os
import subprocess

from datamanager import DataManager

class Task(object):
    
    def __init__(self, command):
        self.command = command

class WorkQueue(list):
    pass

def make_command(input_file, output_file):

    command = ['docker',
               'run',
               '-it',
               '--rm',
               '-v',
               '/Users/hartleym/working/:/working',
                'ctprocessor',
                'python',
                'code/ct_pod_analysis/scripts/isolate_single_seed.py',
                input_file,
                output_file]

    return command

def populate_queue(queue, fn):
    dm = DataManager(fn)

    seeds_dir = dm.spath('seeds')
    isolated_dir = dm.spath('isolated_seeds')
    docker_seeds_dir = '/working/C0000230/seeds'
    docker_isolated_dir = '/working/C0000230/isolated_seeds'

    for seed_file in os.listdir(seeds_dir)[2:3]:

        input_file = os.path.join(docker_seeds_dir, seed_file)
        output_file = os.path.join(docker_isolated_dir, seed_file)

        print input_file, output_file

        command = make_command(input_file, output_file)

        subprocess.call(command)

def main():
    mainqueue = WorkQueue()

    fn = 'data/raw/C0000230.ISQ'

    populate_queue(mainqueue, fn)

    # words = ['once', 'upon', 'a', 'time']
    # command = ['echo', 'hello']

    # for word in words:
    #     command = ['echo', word]
    #     mainqueue.append(Task(command))

    # while len(mainqueue):
    #     task = mainqueue.pop(0)
    #     subprocess.call(task.command)

    #subprocess.call(command)

if __name__ == '__main__':
    main()