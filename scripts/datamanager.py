"""Helper class to manage paths for data."""

import os

import yaml

HERE = os.path.dirname(__file__)
WORKING_BASE = os.path.join(HERE, '..', 'working')

# Start with HERE + /working

# Override with base_file_path

# then env


class DataManager(object):

    def __init__(self, base_file_path, working_base=None):
        self.rawpath = base_file_path
        self.basename = os.path.basename(base_file_path)
        self.name, self.ext = os.path.splitext(self.basename)

        raw_dir = os.path.dirname(self.rawpath)

        project_data_filename = os.path.join(raw_dir, 'project.yml')

        with open(project_data_filename) as f:
            yaml_data = yaml.load(f)

        working_base = yaml_data['working_dir']

        self._basepath = os.path.join(working_base, self.name)

    @property
    def basepath(self):
        return self._basepath

    def spath(self, name):
        return os.path.join(self.basepath, name)
